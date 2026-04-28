import structlog

from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException

from src.repositories import consent_repository
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

    row = consent_repository.get_session_user(conn, normalized_session_uuid)

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
    rows = consent_repository.list_pending_clauses(conn, user_id)
    return format_pending_clauses(rows)


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

    mandatory_clauses = consent_repository.list_current_mandatory_clauses(conn)

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

    return consent_repository.insert_consent_event(
        conn=conn,
        user_id=user_id,
        clause_uuid=clause_uuid,
        policy_version_id=policy_version_id,
        event_action=EVENT_ACTIONS[action],
        source_ip=source_ip,
        user_agent=user_agent,
    )


def submit_consent_batch(
    conn,
    user_id: str,
    actions: list,
    source_ip: str,
    user_agent: str,
) -> list[dict]:
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
        
    return get_pending_consent(conn, user_id)