"""Workspace context middleware."""
from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, status
from loguru import logger


class WorkspaceContext:
    """
    Workspace context for request.

    This can be accessed via request.state.workspace_id in route handlers.
    """

    def __init__(self):
        self.workspace_id: Optional[UUID] = None


async def workspace_context_middleware(request: Request, call_next):
    """
    Middleware to extract workspace context from request.

    Workspace can be provided via:
    1. X-Workspace-ID header
    2. workspace_id query parameter
    3. Path parameter (for workspace-specific routes)

    Sets request.state.workspace_id if workspace is specified.
    """
    workspace_id = None

    # Try to get from header
    workspace_header = request.headers.get("X-Workspace-ID")
    if workspace_header:
        try:
            workspace_id = UUID(workspace_header)
        except ValueError:
            logger.warning(f"Invalid workspace ID in header: {workspace_header}")

    # Try to get from query parameter if not in header
    if not workspace_id:
        workspace_query = request.query_params.get("workspace_id")
        if workspace_query:
            try:
                workspace_id = UUID(workspace_query)
            except ValueError:
                logger.warning(f"Invalid workspace ID in query: {workspace_query}")

    # Set in request state
    request.state.workspace_id = workspace_id

    response = await call_next(request)
    return response


def get_workspace_id_from_request(request: Request) -> Optional[UUID]:
    """
    Get workspace ID from request state.

    Args:
        request: FastAPI request

    Returns:
        Workspace UUID or None
    """
    return getattr(request.state, "workspace_id", None)


def require_workspace_context(request: Request) -> UUID:
    """
    Require workspace context in request.

    Args:
        request: FastAPI request

    Returns:
        Workspace UUID

    Raises:
        HTTPException: If workspace context is not set
    """
    workspace_id = get_workspace_id_from_request(request)
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace context is required. Provide X-Workspace-ID header or workspace_id query parameter.",
        )
    return workspace_id
