"""
Pydantic schemas for the DevOps bot application.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SystemFields(BaseModel):
    """Azure DevOps System fields for a work item."""
    title: str = Field(alias="System.Title")
    state: str = Field(alias="System.State")
    work_item_type: str = Field(alias="System.WorkItemType")
    changed_date: datetime = Field(alias="System.ChangedDate")
    created_date: Optional[datetime] = Field(default=None, alias="System.CreatedDate")
    assigned_to: Optional[str] = Field(default=None, alias="System.AssignedTo")
    description: Optional[str] = Field(default=None, alias="System.Description")
    priority: Optional[int] = Field(default=None, alias="System.Priority")
    tags: Optional[str] = Field(default=None, alias="System.Tags")

    class Config:
        populate_by_name = True


class WorkItem(BaseModel):
    """Azure DevOps work item model."""
    id: int
    rev: int
    fields: SystemFields

    class Config:
        populate_by_name = True


class WorkItemReference(BaseModel):
    """Reference to a work item (used in queries)."""
    id: int
    rev: int


class WorkItemQueryResult(BaseModel):
    """Result from a WIQL query."""
    work_items: list[WorkItemReference] = Field(default_factory=list)
    count: int = 0


class WorkItemsResponse(BaseModel):
    """Response containing a list of work items."""
    value: list[WorkItem] = Field(default_factory=list)
    count: int = 0


class ProjectReference(BaseModel):
    """Azure DevOps project reference."""
    id: str
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None


class ProjectListResponse(BaseModel):
    """Response containing a list of projects."""
    value: list[ProjectReference] = Field(default_factory=list)
    count: int = 0


class AdviceRequest(BaseModel):
    """Request model for getting advice from LLM."""
    text: str = Field(min_length=1, max_length=10000)
    context: Optional[str] = None


class AdviceResponse(BaseModel):
    """Response model for LLM advice."""
    advice: str


class ReviewRequest(BaseModel):
    """Request model for code review."""
    code: str = Field(min_length=1)
    language: Optional[str] = None
    focus_areas: Optional[list[str]] = None


class ReviewResponse(BaseModel):
    """Response model for code review."""
    review: str
    issues: Optional[list[str]] = None


class HealthCheckResult(BaseModel):
    """Result of a health check."""
    project_name: str
    status: str
    details: Optional[dict] = None


class BugSummary(BaseModel):
    """Summary of a bug for display."""
    id: int
    title: str
    state: str
    assigned_to: Optional[str] = None
    priority: Optional[int] = None

    @classmethod
    def from_work_item(cls, work_item: WorkItem) -> "BugSummary":
        """Create a BugSummary from a WorkItem."""
        fields = work_item.fields
        return cls(
            id=work_item.id,
            title=fields.title,
            state=fields.state,
            assigned_to=fields.assigned_to,
            priority=fields.priority,
        )
