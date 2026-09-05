from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.auth import UserResponse
from ..schemas.pagination import PaginatedResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=PaginatedResponse[UserResponse])
def get_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[UserResponse]:
    total = db.scalar(select(func.count()).select_from(User))

    users = db.scalars(
        select(User).order_by(User.id).limit(limit).offset(offset)
    ).all()

    return PaginatedResponse(items=users, total=total, limit=limit, offset=offset)