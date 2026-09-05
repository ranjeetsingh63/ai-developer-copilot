from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Any

from ..database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.repository import Repository
from ..schemas.repository import RepositoryCreate, RepositoryResponse
from ..schemas.pagination import PaginatedResponse
from ..dependencies import get_current_user
from ..services.github import GitHubService
from ..config import settings

router = APIRouter(
    prefix="/projects/{project_id}/repositories",
    tags=["repositories"],
    dependencies=[Depends(get_current_user)]
)


def verify_project_ownership(db: Session, project_id: int, current_user_id: int) -> None:
    """Helper to enforce the explicit 404/403 ownership boundaries."""
    project = db.scalar(select(Project).where(Project.id == project_id))
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this project")


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
async def create_repository(
        project_id: int,
        repo_in: RepositoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Enforce ownership boundaries
    verify_project_ownership(db, project_id, current_user.id)

    # 2. Verify repository existence via GitHub API
    github_svc = GitHubService(settings.github_pat)
    try:
        repo_data = await github_svc.verify_repository(repo_in.github_url)
    finally:
        await github_svc.close()

    # Optional: override or enrich default branch with what GitHub actually reports
    verified_branch = repo_data.get("default_branch", repo_in.default_branch)

    # 3. Create the repository in the database
    new_repo = Repository(
        project_id=project_id,
        github_url=repo_in.github_url,
        name=repo_in.name,
        default_branch=verified_branch
    )
    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)
    return new_repo


@router.get("/", response_model=PaginatedResponse[RepositoryResponse])
def get_repositories(
        project_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
) -> Any:
    # 1. Enforce ownership
    verify_project_ownership(db, project_id, current_user.id)

    # 2. Fetch paginated data
    total = db.scalar(select(func.count()).select_from(Repository).where(Repository.project_id == project_id))
    items = db.scalars(
        select(Repository)
        .where(Repository.project_id == project_id)
        .order_by(Repository.id)
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset
    }