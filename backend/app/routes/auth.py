"""Authentication routes"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, ChangePasswordRequest, RefreshTokenRequest
from app.services.auth import AuthService
from app.exceptions import AuthenticationError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract token from Authorization header"""
    if not authorization:
        raise AuthenticationError("Missing authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")

    return parts[1]


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user = AuthService.register_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
    )
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """Login user and create session"""
    user, access_token, refresh_token = AuthService.login_user(
        db=db,
        username=login_data.username,
        password=login_data.password,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        remember_me=login_data.remember_me,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes in seconds
    )


@router.post("/logout")
async def logout(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
):
    """Logout user and delete session"""
    AuthService.logout_user(db=db, token=token)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token"""
    access_token = AuthService.refresh_access_token(
        db=db,
        refresh_token=refresh_data.refresh_token,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        expires_in=30 * 60,  # 30 minutes in seconds
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
):
    """Get current user information"""
    user = AuthService.get_current_user(db=db, token=token)
    return user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db),
):
    """Change user password"""
    user = AuthService.get_current_user(db=db, token=token)
    AuthService.change_password(
        db=db,
        user_id=str(user.id),
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    return {"message": "Password changed successfully"}
