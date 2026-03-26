from datetime import datetime

from pydantic import BaseModel

from app.models import ProjectStatus, RequirementPriority


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime


class RequirementCreate(BaseModel):
    title: str
    detail: str = ""
    priority: RequirementPriority = RequirementPriority.medium


class TaskCreate(BaseModel):
    title: str


class CompareRequest(BaseModel):
    left_text: str
    right_text: str


class CompareResult(BaseModel):
    overlap_score: float
    left_only: list[str]
    right_only: list[str]
