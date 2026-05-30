import structlog

from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List
from uuid import UUID

from src.api.dependencies.auth import (
    AuthenticatedUser,
    get_current_user,
    get_current_user_no_consent_check,
    require_admin,
    require_admin_or_manager,
)
from src.api.schemas.user_schemas import (
    ProfileResponse,
    UserConsentPreferencesResponse,
    UserConsentUpdateRequest,
    UserConsentUpdateResponse,
    UserCreateRequest,
    UserCreateResponse,
    UserMeResponse,
    UserMeUpdateRequest,
    UserResult,
    UserSetActiveRequest,
    UserUpdateRequest,
)
from src.config.log_events import (
    USER_CREATED,
    USER_UPDATED,
    USER_DEACTIVATED,
    USER_DELETED,
    USER_NOT_FOUND,
    USER_CONFLICT,
    USER_LISTED,
)
from src.database.postgres import get_pg_connection, set_current_user
from src.repositories.user_repository import (
    ProfilePersistenceError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserPersistenceError,
    UserProfileNotFoundError,
)
from src.services.auth_service import admin_invalidate_user_sessions_service
from src.services.consent_service import (
    get_user_consent_preferences,
    update_user_consent_preferences,
)
from src.services.user_service import (
    create_user_service,
    delete_user_service,
    get_current_user_profile_service,
    get_user_by_id_service,
    list_profiles_service,
    list_users_service,
    set_user_active_service,
    update_current_user_profile_service,
    update_user_service,
)

router = APIRouter(prefix="/users", tags=["users"])
log = structlog.get_logger()


@router.get("/", response_model=List[UserResult], status_code=status.HTTP_200_OK)
def list_users(current_user: AuthenticatedUser = Depends(require_admin_or_manager)):
    users = list_users_service()
    log.info(USER_LISTED, count=len(users))
    return users


@router.get("/profiles", response_model=List[ProfileResponse], status_code=status.HTTP_200_OK)
def get_profiles(_current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        profiles = list_profiles_service()
        log.info("profiles.listed", count=len(profiles))
        return [
            ProfileResponse(profile_uuid=p.profile_uuid, profile_name=p.profile_name)
            for p in profiles
        ]
    except ProfilePersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao listar perfis.",
        ) from exc


@router.get("/me", response_model=UserMeResponse, status_code=status.HTTP_200_OK)
def get_my_profile(current_user: AuthenticatedUser = Depends(get_current_user)):
    try:
        return get_current_user_profile_service(current_user.user_id)
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=current_user.user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/me", response_model=UserMeResponse, status_code=status.HTTP_200_OK)
def update_my_profile(
    payload: UserMeUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        result = update_current_user_profile_service(
            current_user.user_id,
            username=payload.username,
            email=str(payload.email),
        )
        log.info(USER_UPDATED, user_id=current_user.user_id, fields_changed=["username", "email"])
        return result
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=current_user.user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        log.warning(USER_CONFLICT, user_id=current_user.user_id, reason=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "/{user_uuid}/consents",
    response_model=UserConsentPreferencesResponse,
    status_code=status.HTTP_200_OK,
    summary="List current consent preferences for the authenticated user",
)
def get_user_consents(
    user_uuid: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    if str(user_uuid) != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cannot_manage_other_user_consents",
        )

    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        consents = get_user_consent_preferences(conn, current_user.user_id)

    return {
        "user_id": current_user.user_id,
        "consents": consents,
    }


@router.patch(
    "/{user_uuid}/consents",
    response_model=UserConsentUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="Update consent preferences for the authenticated user",
    description=(
        "Updates individual consent preferences. Each change is stored as a new "
        "append-only TB_CONSENT_LOG event. If a mandatory clause is revoked, the "
        "user is anonymized and all active sessions are invalidated before the "
        "response is returned."
    ),
)
def patch_user_consents(
    user_uuid: UUID,
    payload: UserConsentUpdateRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    if str(user_uuid) != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cannot_manage_other_user_consents",
        )

    source_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    with get_pg_connection() as conn:
        set_current_user(conn, current_user.user_id)
        return update_user_consent_preferences(
            conn,
            user_id=current_user.user_id,
            updates=payload.consents,
            source_ip=source_ip,
            user_agent=user_agent,
        )


@router.get("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def get_user(user_uuid: UUID, current_user: AuthenticatedUser = Depends(require_admin_or_manager)):
    try:
        return get_user_by_id_service(user_uuid)
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, current_user: AuthenticatedUser = Depends(require_admin)):
    try:
        result = create_user_service(payload)
        log.info(USER_CREATED, actor_id=current_user.user_id, target_user_id=str(result.user_uuid), profile_name=result.profile_name)
        return result
    except UserAlreadyExistsError as exc:
        log.warning(USER_CONFLICT, reason=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        log.warning(USER_NOT_FOUND, reason=str(exc))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao criar usuário.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.patch("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def update_user(
    user_uuid: UUID,
    payload: UserUpdateRequest,
    current_user: AuthenticatedUser = Depends(require_admin),
):
    try:
        data = {"username": payload.username, "profile_name": payload.profile_name}
        result = update_user_service(user_uuid, data)
        log.info(USER_UPDATED, actor_id=current_user.user_id, target_user_id=str(user_uuid), fields_changed=list(data.keys()))
        return result
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        log.warning(USER_CONFLICT, user_id=str(user_uuid), reason=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid), reason=str(exc))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_uuid}/active", response_model=UserResult, status_code=status.HTTP_200_OK)
def set_active(
    user_uuid: UUID,
    payload: UserSetActiveRequest,
    current_user: AuthenticatedUser = Depends(require_admin),
):
    try:
        result = set_user_active_service(user_uuid, payload.active, acting_user_id=current_user.user_id)
        log.info(USER_DEACTIVATED, actor_id=current_user.user_id, target_user_id=str(user_uuid), active=payload.active)
        return result
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_uuid}/sessions", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_sessions(
    user_uuid: UUID,
    current_user: AuthenticatedUser = Depends(require_admin),
):
    admin_invalidate_user_sessions_service(
        target_user_id=str(user_uuid),
        acting_user_id=current_user.user_id,
    )


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_uuid: UUID,
    current_user: AuthenticatedUser = Depends(get_current_user_no_consent_check),
):
    is_self_delete = str(user_uuid) == current_user.user_id
    is_admin = current_user.profile_name == "ADMIN"

    if not is_self_delete and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="cannot_delete_other_user",
        )

    try:
        delete_user_service(user_uuid)
        log.info(USER_DELETED, actor_id=current_user.user_id, target_user_id=str(user_uuid))
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
