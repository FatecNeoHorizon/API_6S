import structlog

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException
from psycopg2 import IntegrityError, OperationalError

from src.config.exception_handlers import handle_db_integrity_error, handle_db_operational_error
from src.repositories import consent_repository
from src.repositories.user_repository import delete_user, invalidate_user_sessions
from src.config.log_events import  CONSENT_REGISTERED, CONSENT_REVOKED

log = structlog.get_logger()


@dataclass
class AuthenticatedUser:
    user_id: str
    session_id: str
    profile_name: str


EVENT_ACTIONS = {
    "CONSENT": "CONSENT_ACCEPTED",
    "REVOCATION": "CONSENT_REVOKED",
}


def resolve_session(conn, session_uuid: str) -> AuthenticatedUser | None:
    """
    Validates the session UUID format and resolves the authenticated user.
    """
    try:
        normalized_session_uuid = str(UUID(session_uuid))
    except ValueError:
        return None

    try:
        row = consent_repository.get_session_user(conn, normalized_session_uuid)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="resolve_session")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="resolve_session")
        raise HTTPException(status_code=503, detail="database_unavailable")

    if not row:
        return None

    return AuthenticatedUser(
        user_id=str(row["user_uuid"]),
        session_id=str(row["session_uuid"]),
        profile_name=row["profile_name"],
    )


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


def get_pending_consent(conn, user_id: str) -> list[dict]:
    """
    Returns formatted pending mandatory consent clauses.
    """
    try:
        rows = consent_repository.list_pending_clauses(conn, user_id)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="get_pending_consent")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="get_pending_consent")
        raise HTTPException(status_code=503, detail="database_unavailable")
    return format_pending_clauses(rows)


def format_consent_history(rows: list[dict]) -> list[dict]:
    return [
        {
            "log_uuid": row["log_uuid"],
            "action": row["action"],
            "registered_at": row["registered_at"],
            "channel": row["channel"],
            "consent_hash": row["consent_hash"],
            "policy_version_id": row["policy_version_id"],
            "policy_type": row["policy_type"],
            "policy_version": row["policy_version"],
            "clause_uuid": row["clause_uuid"],
            "clause_code": row["clause_code"],
            "clause_title": row["clause_title"],
            "mandatory": row["mandatory"],
        }
        for row in rows
    ]


def get_user_consent_history(conn, user_id: str) -> list[dict]:
    """
    Returns immutable consent history for the authenticated user.
    """
    try:
        rows = consent_repository.list_user_consent_history(conn, user_id)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="get_user_consent_history")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="get_user_consent_history")
        raise HTTPException(status_code=503, detail="database_unavailable")

    return format_consent_history(rows)


def format_consent_preferences(rows: list[dict]) -> list[dict]:
    return [
        {
            "clause_id": row["clause_uuid"],
            "policy_version_id": row["policy_version_id"],
            "policy_type": row["policy_type"],
            "policy_version": row["policy_version"],
            "clause_code": row["clause_code"],
            "clause_title": row["clause_title"],
            "clause_description": row.get("clause_description"),
            "mandatory": row["mandatory"],
            "accepted": row["accepted"],
            "current_status": row["current_status"],
            "last_action": row.get("last_action"),
            "last_action_at": row.get("last_action_at"),
        }
        for row in rows
    ]


def get_user_consent_preferences(conn, user_id: str) -> list[dict]:
    """
    Returns all current clauses with the latest consent status for the user.
    """
    try:
        rows = consent_repository.list_user_current_consent_preferences(conn, user_id)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="get_user_consent_preferences")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="get_user_consent_preferences")
        raise HTTPException(status_code=503, detail="database_unavailable")

    return format_consent_preferences(rows)


def update_user_consent_preferences(
    conn,
    *,
    user_id: str,
    updates: list,
    source_ip: str,
    user_agent: str,
) -> dict:
    """
    Updates consent preferences after onboarding.

    Every change is recorded as a new append-only TB_CONSENT_LOG row.
    Revoking a mandatory clause deletes the user through the same soft-delete
    flow used by the account deletion endpoint and invalidates all active
    sessions before the response is returned.
    """
    if not updates:
        raise HTTPException(status_code=422, detail="empty_consent_update")

    seen_clause_ids = set()
    mandatory_revoked = False
    updated_count = 0

    try:
        for item in updates:
            clause_id = str(item.clause_id)

            if clause_id in seen_clause_ids:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "duplicate_clause_id",
                        "clause_id": clause_id,
                    },
                )

            seen_clause_ids.add(clause_id)

            clause = consent_repository.get_current_clause_for_consent_update(
                conn,
                clause_id,
            )

            if not clause:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "invalid_clause_id",
                        "clause_id": clause_id,
                    },
                )

            accepted = bool(item.accepted)
            event_action = "CONSENT_ACCEPTED" if accepted else "CONSENT_REVOKED"

            inserted = consent_repository.insert_consent_event(
                conn=conn,
                user_id=user_id,
                clause_uuid=str(clause["clause_uuid"]),
                policy_version_id=str(clause["policy_version_id"]),
                event_action=event_action,
                source_ip=source_ip,
                user_agent=user_agent,
            )

            if not inserted:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "consent_event_not_inserted",
                        "clause_id": clause_id,
                    },
                )

            updated_count += 1

            if clause["mandatory"] and not accepted:
                mandatory_revoked = True

        if mandatory_revoked:
            deleted = delete_user(conn, user_id)
            if not deleted:
                raise HTTPException(status_code=404, detail="user_not_found")

            invalidate_user_sessions(conn, user_id)

            return {
                "account_deleted": True,
                "updated_count": updated_count,
                "consents": None,
            }

        return {
            "account_deleted": False,
            "updated_count": updated_count,
            "consents": get_user_consent_preferences(conn, user_id),
        }

    except HTTPException:
        raise
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="update_user_consent_preferences")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="update_user_consent_preferences")
        raise HTTPException(status_code=503, detail="database_unavailable")


def _get_action_value(action_item) -> str:
    action = getattr(action_item, "action", None)

    if hasattr(action, "value"):
        return action.value

    return str(action)


def _get_clause_uuid(action_item) -> str:
    return str(getattr(action_item, "clause_uuid"))


def _get_policy_version_id(action_item) -> str:
    return str(getattr(action_item, "policy_version_id"))


def validate_mandatory_acceptance(conn, actions: list) -> None:
    """
    If the payload contains CONSENT actions, all current mandatory clauses must
    be present as CONSENT.
    """
    consent_actions = [
        action_item
        for action_item in actions
        if _get_action_value(action_item) == "CONSENT"
    ]

    if not consent_actions:
        return

    try:
        mandatory_clauses = consent_repository.list_current_mandatory_clauses(conn)
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="validate_mandatory_acceptance")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="validate_mandatory_acceptance")
        raise HTTPException(status_code=503, detail="database_unavailable")

    submitted_clause_ids = {
        _get_clause_uuid(action_item)
        for action_item in consent_actions
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



def submit_consent(
    conn,
    user_id: str,
    clause_uuid: str,
    policy_version_id: str,
    action: str,
    source_ip: str,
    user_agent: str,
) -> bool:
    """
    Maps the user action to an immutable event and inserts it.
    """
    if action not in EVENT_ACTIONS:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "invalid_consent_action",
                "action": action,
            },
        )

    try:
        return consent_repository.insert_consent_event(
            conn=conn,
            user_id=user_id,
            clause_uuid=clause_uuid,
            policy_version_id=policy_version_id,
            event_action=EVENT_ACTIONS[action],
            source_ip=source_ip,
            user_agent=user_agent,
        )
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="submit_consent")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="submit_consent")
        raise HTTPException(status_code=503, detail="database_unavailable")


def submit_consent_batch(
    conn,
    user_id: str,
    actions: list,
    source_ip: str,
    user_agent: str,
) -> list[dict]:
    try:
        validate_mandatory_acceptance(conn, actions)

        for action_item in actions:
            clause_uuid = _get_clause_uuid(action_item)
            policy_version_id = _get_policy_version_id(action_item)
            action = _get_action_value(action_item)

            inserted = submit_consent(
                conn=conn,
                user_id=user_id,
                clause_uuid=clause_uuid,
                policy_version_id=policy_version_id,
                action=action,
                source_ip=source_ip,
                user_agent=user_agent,
            )

            if not inserted:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "code": "invalid_clause_or_policy_version",
                        "clause_uuid": clause_uuid,
                        "policy_version_id": policy_version_id,
                    },
                )
            event = CONSENT_REGISTERED if action == "CONSENT" else CONSENT_REVOKED
            log.info(event, user_id=user_id, clause_id=clause_uuid, channel="WEB")
    except HTTPException:
        raise
    except IntegrityError as exc:
        handle_db_integrity_error(exc, context="submit_consent_batch")
        raise HTTPException(status_code=409, detail="conflict")
    except OperationalError as exc:
        handle_db_operational_error(exc, context="submit_consent_batch")
        raise HTTPException(status_code=503, detail="database_unavailable")
        
    return get_pending_consent(conn, user_id)
