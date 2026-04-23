from fastapi import APIRouter, HTTPException, status
from typing import List

from src.api.schemas.user_schemas import ProfileResponse, UserCreateRequest, UserCreateResponse
from src.repositories.user_repository import (
    ProfilePersistenceError,
    UserAlreadyExistsError,
    UserPersistenceError,
    UserProfileNotFoundError,
    list_profiles,
)
from src.services.user_service import create_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profiles", response_model=List[ProfileResponse], status_code=status.HTTP_200_OK)
def get_profiles() -> List[ProfileResponse]:
    try:
        profiles = list_profiles()
        return [
            ProfileResponse(profile_uuid=p.profile_uuid, profile_name=p.profile_name)
            for p in profiles
        ]
    except ProfilePersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list profiles.",
        ) from exc


@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateRequest) -> UserCreateResponse:
    try:
        return create_user_service(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except UserProfileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UserPersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user.",
        ) from exc
