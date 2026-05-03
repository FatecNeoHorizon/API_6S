import structlog

from fastapi import APIRouter, HTTPException, Request, status
from typing import List
from uuid import UUID

from src.api.schemas.user_schemas import (
    ProfileResponse, UserCreateRequest, UserCreateResponse,
    UserResult, UserUpdateRequest, UserSetActiveRequest,
)
from src.config.log_events import (
    USER_CREATED, USER_UPDATED, USER_DEACTIVATED,
    USER_DELETED, USER_NOT_FOUND, USER_CONFLICT, USER_LISTED,
)
from src.repositories.user_repository import (
    ProfilePersistenceError, UserAlreadyExistsError, UserNotFoundError,
    UserPersistenceError, UserProfileNotFoundError,
)
from src.services.user_service import (
    create_user_service, list_profiles_service, get_user_by_id_service,
    list_users_service, update_user_service, set_user_active_service,
    delete_user_service,
)

router = APIRouter(prefix="/users", tags=["users"])
log = structlog.get_logger()

@router.get("/", response_model=List[UserResult], status_code=status.HTTP_200_OK)
def list_users():
    users = list_users_service()
    log.info(USER_LISTED, count=len(users))
    return users


@router.get("/profiles", response_model=List[ProfileResponse], status_code=status.HTTP_200_OK)
def get_profiles():
    try:
        profiles = list_profiles_service()
        log.info("profiles.listed", count=len(profiles))
        return [ProfileResponse(profile_uuid=p.profile_uuid, profile_name=p.profile_name) for p in profiles]
    except ProfilePersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao listar perfis.") from exc


@router.get("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def get_user(user_uuid: UUID):
    try:
        return get_user_by_id_service(user_uuid)
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest, request: Request):
    try:
        source_ip = request.client.host if request.client else "0.0.0.0"
        user_agent = request.headers.get("user-agent", "")
        result = create_user_service(payload, source_ip=source_ip, user_agent=user_agent)
        log.info(USER_CREATED, user_id=str(result.user_uuid), profile_id=str(result.profile_id))
        return result
    except UserAlreadyExistsError as exc:
        log.warning(USER_CONFLICT, reason=str(exc))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        log.warning(USER_NOT_FOUND, reason=str(exc))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserPersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao criar usuário.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

@router.patch("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def update_user(user_uuid: UUID, payload: UserUpdateRequest):
    try:
        data = {"username": payload.username, "profile_id": payload.profile_id}
        result = update_user_service(user_uuid, data)
        log.info(USER_UPDATED, user_id=str(user_uuid), fields_changed=list(data.keys()))
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
def set_active(user_uuid: UUID, payload: UserSetActiveRequest):
    try:
        result = set_user_active_service(user_uuid, payload.active)
        log.info(USER_DEACTIVATED, user_id=str(user_uuid), active=payload.active)
        return result
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_uuid: UUID):
    try:
        delete_user_service(user_uuid)
        log.info(USER_DELETED, user_id=str(user_uuid))
    except UserNotFoundError as exc:
        log.warning(USER_NOT_FOUND, user_id=str(user_uuid))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
