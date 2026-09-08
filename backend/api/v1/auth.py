from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from core.config import settings
from core.security import create_access_token, verify_password
from crud.users import create_user, get_user_by_email
from models.user import User
from schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    existing_user = await get_user_by_email(session, user_data.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    return await create_user(session, user_data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_user(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user = await get_user_by_email(session, credentials.email)
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        subject=str(user.id),
        expires_minutes=settings.access_token_expire_minutes,
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user
