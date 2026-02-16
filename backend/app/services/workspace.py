"""Workspace service."""
import re
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from loguru import logger

from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRole
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceMemberCreate


class WorkspaceService:
    """Workspace service for managing workspaces and members."""

    def __init__(self, db: AsyncSession):
        """Initialize workspace service."""
        self.db = db

    def _slugify(self, text: str) -> str:
        """
        Convert text to slug format.

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        text = re.sub(r'^-+|-+$', '', text)
        return text

    async def create_workspace(self, data: WorkspaceCreate, owner_id: UUID) -> Workspace:
        """
        Create a new workspace.

        Args:
            data: Workspace creation data
            owner_id: UUID of the workspace owner

        Returns:
            Created workspace

        Raises:
            HTTPException: If slug already exists
        """
        # Generate slug from name if not provided
        slug = data.slug if data.slug else self._slugify(data.name)

        # Check if slug already exists
        query = select(Workspace).where(Workspace.slug == slug)
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            # Try adding a number suffix
            counter = 1
            while existing:
                new_slug = f"{slug}-{counter}"
                query = select(Workspace).where(Workspace.slug == new_slug)
                result = await self.db.execute(query)
                existing = result.scalar_one_or_none()
                if not existing:
                    slug = new_slug
                    break
                counter += 1

        # Create workspace
        workspace = Workspace(
            name=data.name,
            slug=slug,
            owner_id=owner_id,
            settings={},
            metadata={}
        )

        self.db.add(workspace)
        await self.db.flush()

        # Add owner as workspace member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=WorkspaceRole.OWNER
        )
        self.db.add(member)

        await self.db.commit()
        await self.db.refresh(workspace)

        logger.info(f"Workspace created: {workspace.name} ({workspace.slug})")

        return workspace

    async def get_workspace(self, workspace_id: UUID) -> Optional[Workspace]:
        """
        Get workspace by ID.

        Args:
            workspace_id: Workspace UUID

        Returns:
            Workspace or None
        """
        query = select(Workspace).where(Workspace.id == workspace_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_workspace_by_slug(self, slug: str) -> Optional[Workspace]:
        """
        Get workspace by slug.

        Args:
            slug: Workspace slug

        Returns:
            Workspace or None
        """
        query = select(Workspace).where(Workspace.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_workspaces(self, user_id: UUID) -> List[Workspace]:
        """
        Get all workspaces for a user.

        Args:
            user_id: User UUID

        Returns:
            List of workspaces
        """
        query = (
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_workspace(
        self,
        workspace_id: UUID,
        data: WorkspaceUpdate,
        user_id: UUID
    ) -> Workspace:
        """
        Update workspace.

        Args:
            workspace_id: Workspace UUID
            data: Update data
            user_id: User making the update

        Returns:
            Updated workspace

        Raises:
            HTTPException: If workspace not found or user lacks permission
        """
        # Get workspace
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Check if user has permission (owner or admin)
        has_permission = await self.check_workspace_permission(
            workspace_id,
            user_id,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        # Update fields
        if data.name is not None:
            workspace.name = data.name
        if data.settings is not None:
            workspace.settings = data.settings
        if data.sso_enabled is not None:
            workspace.sso_enabled = data.sso_enabled
        if data.sso_enforced is not None:
            workspace.sso_enforced = data.sso_enforced

        await self.db.commit()
        await self.db.refresh(workspace)

        logger.info(f"Workspace updated: {workspace.id}")

        return workspace

    async def delete_workspace(self, workspace_id: UUID, user_id: UUID) -> None:
        """
        Delete workspace.

        Args:
            workspace_id: Workspace UUID
            user_id: User requesting deletion

        Raises:
            HTTPException: If workspace not found or user is not owner
        """
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Only owner can delete workspace
        if workspace.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only workspace owner can delete the workspace"
            )

        await self.db.delete(workspace)
        await self.db.commit()

        logger.info(f"Workspace deleted: {workspace_id}")

    async def add_member(
        self,
        workspace_id: UUID,
        data: WorkspaceMemberCreate,
        inviter_id: UUID
    ) -> WorkspaceMember:
        """
        Add member to workspace.

        Args:
            workspace_id: Workspace UUID
            data: Member data
            inviter_id: User adding the member

        Returns:
            Workspace member

        Raises:
            HTTPException: If workspace not found, user not found, or insufficient permissions
        """
        # Check workspace exists
        workspace = await self.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )

        # Check inviter has permission
        has_permission = await self.check_workspace_permission(
            workspace_id,
            inviter_id,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add members"
            )

        # Get user to add
        if not data.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )

        user_query = select(User).where(User.id == data.user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if already a member
        existing_query = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == data.user_id
            )
        )
        existing_result = await self.db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member"
            )

        # Add member
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=data.user_id,
            role=WorkspaceRole(data.role) if data.role else WorkspaceRole.MEMBER
        )

        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)

        logger.info(f"Member added to workspace {workspace_id}: {data.user_id}")

        return member

    async def remove_member(
        self,
        workspace_id: UUID,
        member_id: UUID,
        remover_id: UUID
    ) -> None:
        """
        Remove member from workspace.

        Args:
            workspace_id: Workspace UUID
            member_id: Member UUID to remove
            remover_id: User removing the member

        Raises:
            HTTPException: If member not found or insufficient permissions
        """
        # Get member
        query = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.id == member_id
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # Cannot remove workspace owner
        if member.role == WorkspaceRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove workspace owner"
            )

        # Check permission
        has_permission = await self.check_workspace_permission(
            workspace_id,
            remover_id,
            [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        await self.db.delete(member)
        await self.db.commit()

        logger.info(f"Member removed from workspace {workspace_id}: {member.user_id}")

    async def get_workspace_members(self, workspace_id: UUID) -> List[WorkspaceMember]:
        """
        Get all members of a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            List of workspace members
        """
        query = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .order_by(WorkspaceMember.created_at)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def check_workspace_permission(
        self,
        workspace_id: UUID,
        user_id: UUID,
        required_roles: Optional[List[WorkspaceRole]] = None
    ) -> bool:
        """
        Check if user has permission in workspace.

        Args:
            workspace_id: Workspace UUID
            user_id: User UUID
            required_roles: List of acceptable roles

        Returns:
            True if user has permission, False otherwise
        """
        query = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            return False

        if required_roles and member.role not in required_roles:
            return False

        return True

    async def get_user_workspace_role(
        self,
        workspace_id: UUID,
        user_id: UUID
    ) -> Optional[WorkspaceRole]:
        """
        Get user's role in workspace.

        Args:
            workspace_id: Workspace UUID
            user_id: User UUID

        Returns:
            WorkspaceRole or None
        """
        query = select(WorkspaceMember).where(
            and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        member = result.scalar_one_or_none()

        return member.role if member else None
