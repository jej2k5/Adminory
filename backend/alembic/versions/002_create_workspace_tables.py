"""Create workspace tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-16 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create workspace_plan enum
    workspace_plan_enum = postgresql.ENUM(
        'free',
        'pro',
        'enterprise',
        name='workspaceplan',
        create_type=True
    )
    workspace_plan_enum.create(op.get_bind(), checkfirst=True)

    # Create workspace_role enum
    workspace_role_enum = postgresql.ENUM(
        'owner',
        'admin',
        'member',
        'viewer',
        name='workspacerole',
        create_type=True
    )
    workspace_role_enum.create(op.get_bind(), checkfirst=True)

    # Create workspaces table
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('plan', workspace_plan_enum, nullable=False, server_default='free'),
        sa.Column('sso_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sso_enforced', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', postgresql.JSON(), nullable=True),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes
    op.create_index('ix_workspaces_id', 'workspaces', ['id'])
    op.create_index('ix_workspaces_slug', 'workspaces', ['slug'])
    op.create_index('ix_workspaces_owner_id', 'workspaces', ['owner_id'])

    # Create workspace_members table
    op.create_table(
        'workspace_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', workspace_role_enum, nullable=False, server_default='member'),
        sa.Column('permissions', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint('workspace_id', 'user_id', name='uq_workspace_member')
    )

    # Create indexes
    op.create_index('ix_workspace_members_id', 'workspace_members', ['id'])
    op.create_index('ix_workspace_members_workspace_id', 'workspace_members', ['workspace_id'])
    op.create_index('ix_workspace_members_user_id', 'workspace_members', ['user_id'])


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop indexes
    op.drop_index('ix_workspace_members_user_id', table_name='workspace_members')
    op.drop_index('ix_workspace_members_workspace_id', table_name='workspace_members')
    op.drop_index('ix_workspace_members_id', table_name='workspace_members')

    op.drop_index('ix_workspaces_owner_id', table_name='workspaces')
    op.drop_index('ix_workspaces_slug', table_name='workspaces')
    op.drop_index('ix_workspaces_id', table_name='workspaces')

    # Drop tables
    op.drop_table('workspace_members')
    op.drop_table('workspaces')

    # Drop enum types
    workspace_role_enum = postgresql.ENUM(
        'owner',
        'admin',
        'member',
        'viewer',
        name='workspacerole'
    )
    workspace_role_enum.drop(op.get_bind(), checkfirst=True)

    workspace_plan_enum = postgresql.ENUM(
        'free',
        'pro',
        'enterprise',
        name='workspaceplan'
    )
    workspace_plan_enum.drop(op.get_bind(), checkfirst=True)
