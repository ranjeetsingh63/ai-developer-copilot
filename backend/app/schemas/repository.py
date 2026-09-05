from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class RepositoryCreate(BaseModel):
    github_url: str = Field(
        ...,
        pattern=r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$",
        description="Must be a valid HTTPS GitHub repository URL"
    )
    name: str = Field(..., min_length=1, max_length=100)
    default_branch: str = Field(default="main", min_length=1, max_length=50)

class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    github_url: str
    name: str
    default_branch: str
    created_at: datetime

    # Pydantic v2 syntax to tell it to read data even if it's not a dict (like our SQLAlchemy model)
    model_config = ConfigDict(from_attributes=True)