from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Project, User
from ..schemas.pagination import PaginatedResponse
from ..schemas.project import ProjectCreate, ProjectResponse


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    new_project = Project(
        name=project_data.name,
        owner_id=current_user.id,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@router.get(
    "/",
    response_model=PaginatedResponse[ProjectResponse],
)
def list_projects(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ProjectResponse]:
    total = db.scalar(
        select(func.count())
        .select_from(Project)
        .where(Project.owner_id == current_user.id)
    )

    projects = db.scalars(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(Project.id)
        .limit(limit)
        .offset(offset)
    ).all()

    return PaginatedResponse(items=projects, total=total, limit=limit, offset=offset)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectResponse:
    project = db.scalar(
        select(Project).where(Project.id == project_id)
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    return project