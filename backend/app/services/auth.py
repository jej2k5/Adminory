"""Authentication service."""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from loguru import logger

from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.redis import get_redis


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service."""
        self.db = db

    async def register_user(self, data: RegisterRequest) -> User:
        """
        Register a new user.

        Args:
            data: Registration data

        Returns:
            Created user

        Raises:
            HTTPException: If email already exists
        """
        # Check if email exists
        query = select(User).where(User.email == data.email)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
            role=UserRole.USER,
            is_active=True,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User registered: {user.email}")

        # TODO: Send verification email
        # from app.tasks.email import send_verification_email
        # verification_token = await self.create_verification_token(user.id)
        # send_verification_email.delay(user.email, verification_token)

        return user

    async def authenticate_user(self, data: LoginRequest) -> Tuple[User, str, str]:
        """
        Authenticate user and generate tokens.

        Args:
            data: Login credentials

        Returns:
            Tuple of (user, access_token, refresh_token)

        Raises:
            HTTPException: If authentication fails
        """
        # Get user by email
        query = select(User).where(User.email == data.email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not user.password_hash or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.commit()

        # Generate tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Store refresh token in Redis (for revocation)
        await self._store_refresh_token(str(user.id), refresh_token)

        logger.info(f"User authenticated: {user.email}")

        return user, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            HTTPException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # Check if refresh token is valid in Redis
        is_valid = await self._check_refresh_token(user_id, refresh_token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )

        # Get user from database
        query = select(User).where(User.id == UUID(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
        }

        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        # Revoke old refresh token and store new one
        await self._revoke_refresh_token(user_id, refresh_token)
        await self._store_refresh_token(user_id, new_refresh_token)

        logger.info(f"Token refreshed for user: {user.email}")

        return new_access_token, new_refresh_token

    async def logout_user(self, user_id: str, refresh_token: str) -> None:
        """
        Logout user by revoking refresh token.

        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke
        """
        await self._revoke_refresh_token(user_id, refresh_token)
        logger.info(f"User logged out: {user_id}")

    async def verify_email(self, token: str) -> User:
        """
        Verify user email address.

        Args:
            token: Verification token

        Returns:
            Updated user

        Raises:
            HTTPException: If token is invalid
        """
        # Decode verification token from Redis
        redis = await get_redis()
        user_id = await redis.get(f"email_verification:{token}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )

        # Get user
        query = select(User).where(User.id == UUID(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update user
        user.email_verified_at = datetime.utcnow()
        await self.db.commit()

        # Delete verification token
        await redis.delete(f"email_verification:{token}")

        logger.info(f"Email verified for user: {user.email}")

        return user

    async def create_password_reset_token(self, email: str) -> str:
        """
        Create password reset token.

        Args:
            email: User email

        Returns:
            Reset token

        Raises:
            HTTPException: If user not found
        """
        # Get user
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal that user doesn't exist (security)
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return ""

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # Store in Redis with 1 hour expiration
        redis = await get_redis()
        await redis.setex(
            f"password_reset:{reset_token}",
            3600,  # 1 hour
            str(user.id)
        )

        logger.info(f"Password reset token created for user: {user.email}")

        # TODO: Send reset email
        # from app.tasks.email import send_password_reset_email
        # send_password_reset_email.delay(user.email, reset_token)

        return reset_token

    async def reset_password(self, token: str, new_password: str) -> User:
        """
        Reset user password.

        Args:
            token: Reset token
            new_password: New password

        Returns:
            Updated user

        Raises:
            HTTPException: If token is invalid
        """
        # Get user ID from Redis
        redis = await get_redis()
        user_id = await redis.get(f"password_reset:{token}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Get user
        query = select(User).where(User.id == UUID(user_id))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update password
        user.password_hash = hash_password(new_password)
        await self.db.commit()

        # Delete reset token
        await redis.delete(f"password_reset:{token}")

        # Revoke all refresh tokens for security
        await self._revoke_all_refresh_tokens(str(user.id))

        logger.info(f"Password reset for user: {user.email}")

        return user

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> User:
        """
        Change user password.

        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password

        Returns:
            Updated user

        Raises:
            HTTPException: If current password is incorrect
        """
        # Get user
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not user.password_hash or not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.password_hash = hash_password(new_password)
        await self.db.commit()

        logger.info(f"Password changed for user: {user.email}")

        return user

    # Private helper methods for refresh token management

    async def _store_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Store refresh token in Redis."""
        redis = await get_redis()
        # Store for 7 days (same as refresh token expiration)
        await redis.setex(
            f"refresh_token:{user_id}:{refresh_token}",
            7 * 24 * 3600,
            "1"
        )

    async def _check_refresh_token(self, user_id: str, refresh_token: str) -> bool:
        """Check if refresh token is valid."""
        redis = await get_redis()
        exists = await redis.exists(f"refresh_token:{user_id}:{refresh_token}")
        return bool(exists)

    async def _revoke_refresh_token(self, user_id: str, refresh_token: str) -> None:
        """Revoke a specific refresh token."""
        redis = await get_redis()
        await redis.delete(f"refresh_token:{user_id}:{refresh_token}")

    async def _revoke_all_refresh_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        redis = await get_redis()
        # Find all keys for this user
        pattern = f"refresh_token:{user_id}:*"
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break

    async def create_verification_token(self, user_id: UUID) -> str:
        """Create email verification token."""
        token = secrets.token_urlsafe(32)
        redis = await get_redis()
        # Store for 24 hours
        await redis.setex(f"email_verification:{token}", 86400, str(user_id))
        return token
