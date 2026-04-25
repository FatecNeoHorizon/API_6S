from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from src.api.schemas.user_schemas import (
    ProfileResponse, UserCreateRequest, UserCreateResponse,
    UserResult, UserUpdateRequest, UserSetActiveRequest,
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


@router.get("/profiles", response_model=List[ProfileResponse], status_code=status.HTTP_200_OK)
def get_profiles():
    try:
        profiles = list_profiles_service()
        return [ProfileResponse(profile_uuid=p.profile_uuid, profile_name=p.profile_name) for p in profiles]
    except ProfilePersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list profiles.") from exc


@router.get("/", response_model=List[UserResult], status_code=status.HTTP_200_OK)
def list_users():
    return list_users_service()


@router.get("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def get_user(user_uuid: UUID):
    try:
        return get_user_by_id_service(user_uuid)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest):
    try:
        return create_user_service(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserPersistenceError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user.") from exc


@router.patch("/{user_uuid}", response_model=UserResult, status_code=status.HTTP_200_OK)
def update_user(user_uuid: UUID, payload: UserUpdateRequest):
    try:
        return update_user_service(user_uuid, {"username": payload.username, "profile_id": payload.profile_id})
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{user_uuid}/active", response_model=UserResult, status_code=status.HTTP_200_OK)
def set_active(user_uuid: UUID, payload: UserSetActiveRequest):
    try:
        return set_user_active_service(user_uuid, payload.active)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{user_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_uuid: UUID):
    try:
        delete_user_service(user_uuid)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc