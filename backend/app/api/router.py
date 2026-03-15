from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.db.models import User
from app.api.queries import router as queries_router
from app.api.results import router as results_router
from app.api.sessions import router as sessions_router

router = APIRouter(prefix="/api/v1", tags=["api"])

# Sub-routers
router.include_router(queries_router)
router.include_router(results_router)
router.include_router(sessions_router)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
