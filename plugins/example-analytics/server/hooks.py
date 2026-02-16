"""Example Analytics Plugin - Lifecycle Hooks."""
from typing import Any
from loguru import logger


async def on_user_login(user: Any) -> None:
    """
    Hook called when a user logs in.

    This example hook logs the login event. In a real plugin,
    you might track this in an analytics database.

    Args:
        user: User object who logged in
    """
    logger.info(f"[Example Analytics] User logged in: {user.email}")

    # Example: Track login in analytics
    # await track_event("user_login", {
    #     "user_id": user.id,
    #     "email": user.email,
    #     "timestamp": datetime.utcnow(),
    # })
