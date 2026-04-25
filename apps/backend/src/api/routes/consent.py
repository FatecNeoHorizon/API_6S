from fastapi import APIRouter, Depends, HTTPException, Request

from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from src.api.schemas.consent import ConsentRequest
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.consent_repository import (
    insert_consent_event,
    list_current_mandatory_clauses,
    list_pending_clauses,
)


router = APIRouter(prefix="/consent", tags=["consent"])


def format_pending_clauses(rows: list[dict]) -> list[dict]:
    return [
        {
            "clause_uuid": str(row["clause_uuid"]),
            "policy_version_id": str(row["policy_version_id"]),
            "policy_type": row["policy_type"],
            "version": row["version"],
            "code": row["clause_code"],
            "title": row["clause_title"],
            "description": row["clause_description"],
            "mandatory": row["mandatory"],
            "display_order": row["display_order"],
        }
        for row in rows
    ]


@router.get("/pending")
def get_pending_consent(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        pending = list_pending_clauses(conn, current_user.user_id)

    return {"pending_clauses": format_pending_clauses(pending)}


@router.post("")
def post_consent(
    payload: ConsentRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)

        consent_actions = [
            action for action in payload.actions if action.action.value == "CONSENT"
        ]

        if consent_actions:
            mandatory_clauses = list_current_mandatory_clauses(conn)

            submitted_clause_ids = {
                str(action.clause_uuid) for action in consent_actions
            }

            missing = [
                {
                    "clause_uuid": str(row["clause_uuid"]),
                    "policy_version_id": str(row["policy_version_id"]),
                    "policy_type": row["policy_type"],
                    "version": row["version"],
                    "code": row["code"],
                    "title": row["title"],
                }
                for row in mandatory_clauses
                if str(row["clause_uuid"]) not in submitted_clause_ids
            ]

            if missing:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "missing_mandatory_clauses",
                        "missing_clauses": missing,
                    },
                )

        for action in payload.actions:
            inserted = insert_consent_event(
                conn=conn,
                user_id=current_user.user_id,
                clause_uuid=str(action.clause_uuid),
                policy_version_id=str(action.policy_version_id),
                action=action.action.value,
                source_ip=source_ip,
                user_agent=user_agent,
            )

            if not inserted:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "invalid_clause_or_policy_version",
                        "clause_uuid": str(action.clause_uuid),
                        "policy_version_id": str(action.policy_version_id),
                    },
                )

        pending = list_pending_clauses(conn, current_user.user_id)

    return {
        "status": "ok",
        "pending_clauses": format_pending_clauses(pending),
    }