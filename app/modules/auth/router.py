from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from .schema import RegisterRequest, UpdateUser, UserResponse, TokenResponse
from .service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user,
    get_current_active_user,
)
from .models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """Register a new user"""
    user = create_user(session, user_data)
    return user


@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user profile"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    user_data: UpdateUser,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update current authenticated user profile"""
    updated_user = update_user(session, current_user.id, user_data)
    return updated_user

