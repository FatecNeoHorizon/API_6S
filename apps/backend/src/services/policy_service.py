from datetime import datetime, timezone

from fastapi import HTTPException

from src.repositories import policy_repository


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def format_policy_version(row: dict) -> dict:
    return {
        "policy_version_id": str(row["version_uuid"]),
        "version": row["version"],
        "policy_type": row["policy_type"],
        "content": row.get("content"),
        "effective_from": row["effective_from"].isoformat(),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


def format_policy_version_summary(row: dict) -> dict:
    return {
        "policy_version_id": str(row["version_uuid"]),
        "version": row["version"],
        "policy_type": row["policy_type"],
        "effective_from": row["effective_from"].isoformat(),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
        "clause_count": int(row["clause_count"]),
    }


def format_clause(row: dict) -> dict:
    return {
        "clause_uuid": str(row["clause_uuid"]),
        "policy_version_id": str(row["policy_version_id"]),
        "code": row["code"],
        "title": row["title"],
        "description": row["description"],
        "mandatory": row["mandatory"],
        "display_order": row["display_order"],
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


def get_current_terms(conn) -> dict:
    rows = policy_repository.list_current_terms(conn)

    versions: dict[str, dict] = {}

    for row in rows:
        version_id = str(row["version_uuid"])

        if version_id not in versions:
            versions[version_id] = {
                "policy_version_id": version_id,
                "version": row["version"],
                "policy_type": row["policy_type"],
                "content": row["content"],
                "effective_from": row["effective_from"].isoformat(),
                "clauses": [],
            }

        if row["clause_uuid"] is not None:
            versions[version_id]["clauses"].append(
                {
                    "clause_uuid": str(row["clause_uuid"]),
                    "code": row["code"],
                    "title": row["title"],
                    "description": row["description"],
                    "mandatory": row["mandatory"],
                    "display_order": row["display_order"],
                }
            )

    return {"terms": list(versions.values())}


def create_policy_version(
    conn,
    version: str,
    policy_type: str,
    content: str,
    effective_from: datetime,
) -> dict:
    effective_from = normalize_datetime(effective_from)
    now = datetime.now(timezone.utc)

    if effective_from <= now:
        raise HTTPException(
            status_code=422,
            detail="effective_from_must_be_future",
        )

    if policy_repository.policy_version_exists(
        conn,
        version=version,
        policy_type=policy_type,
    ):
        raise HTTPException(
            status_code=409,
            detail="policy_version_already_exists",
        )

    created = policy_repository.create_policy_version(
        conn=conn,
        version=version,
        policy_type=policy_type,
        content=content,
        effective_from=effective_from,
    )

    return format_policy_version(created)


def list_policy_versions(conn) -> dict:
    versions = policy_repository.list_policy_versions(conn)

    return {
        "versions": [
            format_policy_version_summary(version)
            for version in versions
        ]
    }


def create_clause(
    conn,
    version_id: str,
    code: str,
    title: str,
    description: str | None,
    mandatory: bool,
    display_order: int,
) -> dict:
    now = datetime.now(timezone.utc)

    version = policy_repository.get_policy_version(conn, version_id)

    if not version:
        raise HTTPException(
            status_code=404,
            detail="policy_version_not_found",
        )

    effective_from = normalize_datetime(version["effective_from"])

    if effective_from <= now:
        raise HTTPException(
            status_code=422,
            detail="cannot_add_clause_to_effective_version",
        )

    if policy_repository.clause_code_exists(conn, version_id, code):
        raise HTTPException(
            status_code=409,
            detail="clause_code_already_exists_for_this_version",
        )

    created = policy_repository.create_clause(
        conn=conn,
        version_id=version_id,
        code=code,
        title=title,
        description=description,
        mandatory=mandatory,
        display_order=display_order,
    )

    return format_clause(created)


def list_clauses(conn, version_id: str) -> dict:
    version = policy_repository.get_policy_version(conn, version_id)

    if not version:
        raise HTTPException(
            status_code=404,
            detail="policy_version_not_found",
        )

    clauses = policy_repository.list_clauses(conn, version_id)

    return {
        "clauses": [
            format_clause(clause)
            for clause in clauses
        ]
    }


def get_policy_version(conn, version_id: str) -> dict:
    """Return a full policy version including content."""
    version = policy_repository.get_policy_version(conn, version_id)

    if not version:
        raise HTTPException(status_code=404, detail="policy_version_not_found")

    return format_policy_version(version)