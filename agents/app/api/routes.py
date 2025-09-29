"""
API routes for the agent service
"""

from fastapi import APIRouter

from app.api.endpoints import chat, capabilities

router = APIRouter()

# Include endpoint routers
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(capabilities.router, prefix="/capabilities", tags=["capabilities"])