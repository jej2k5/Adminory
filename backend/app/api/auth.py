"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    TokenResponse,
    RefreshTokenRequest,
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        data: Registration data
        db: Database session

    Returns:
        Success message with user ID
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(data)

    return {
        "message": "User registered successfully. Please verify your email.",
        "user_id": str(user.id),
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.

    Args:
        data: Login credentials
        db: Database session

    Returns:
        Authentication response with tokens and user data
    """
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.authenticate_user(data)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Args:
        data: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens
    """
    auth_service = AuthService(db)
    access_token, refresh_token = await auth_service.refresh_access_token(data.refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", response_model=dict)
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking refresh token.

    Args:
        refresh_token: Refresh token to revoke
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    await auth_service.logout_user(str(current_user.id), refresh_token)

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user data
    """
    return UserResponse.model_validate(current_user)


@router.post("/verify-email", response_model=dict)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user email address.

    Args:
        data: Verification token
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    user = await auth_service.verify_email(data.token)

    return {
        "message": "Email verified successfully",
        "email": user.email,
    }


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset email.

    Args:
        data: User email
        db: Database session

    Returns:
        Success message (always, for security)
    """
    auth_service = AuthService(db)
    await auth_service.create_password_reset_token(data.email)

    # Always return success (don't reveal if email exists)
    return {
        "message": "If the email exists, a password reset link has been sent."
    }


@router.post("/reset-password", response_model=dict)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using reset token.

    Args:
        data: Reset token and new password
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    user = await auth_service.reset_password(data.token, data.new_password)

    return {
        "message": "Password reset successfully",
        "email": user.email,
    }


@router.post("/change-password", response_model=dict)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for authenticated user.

    Args:
        data: Current and new password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    auth_service = AuthService(db)
    await auth_service.change_password(
        current_user.id,
        data.current_password,
        data.new_password,
    )

    return {"message": "Password changed successfully"}
