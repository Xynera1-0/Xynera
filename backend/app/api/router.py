from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.db.models import User

router = APIRouter(prefix="/api/v1", tags=["api"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
