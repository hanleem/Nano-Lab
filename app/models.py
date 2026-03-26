from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class ProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    completed = "completed"


class RequirementPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = ""
    status: ProjectStatus = Field(default=ProjectStatus.draft)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    filename: str
    extracted_text: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Requirement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    title: str
    detail: str = ""
    priority: RequirementPriority = Field(default=RequirementPriority.medium)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    title: str
    done: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
