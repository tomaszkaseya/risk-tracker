from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional, List

# This file is structured to avoid circular dependencies between schemas.
# 1. Base schemas: Contain fields for creation, no ID or relationships.
# 2. Create/Update schemas: Inherit from Base, used for API input.
# 3. Response schemas: Used for API output, may contain relationships to other schemas.
#    - To prevent recursion, we define simplified "ForNesting" schemas.

# --- Simplified Schemas for Nested Responses ---

class ProjectForEpic(BaseModel):
    """A minimal Project representation for nesting inside an Epic response."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class EpicForProject(BaseModel):
    """A minimal Epic representation for nesting inside a Project response."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    status: str

class RiskUpdateResponse(BaseModel):
    """The full response for a risk update."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    risk_id: int
    update_text: str
    date_added: date
    created_at: datetime

# --- Full Schemas with Relationships ---

class Risk(BaseModel):
    """The full response for a Risk, including its updates."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    epic_id: int
    description: str
    mitigation_plan: Optional[str] = None
    date_added: date
    status: str
    created_at: datetime
    updated_at: datetime
    updates: List[RiskUpdateResponse] = []

class Epic(BaseModel):
    """The full response for an Epic, including its project and risks."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: Optional[str] = None
    target_launch_date: Optional[date] = None
    actual_launch_date: Optional[date] = None
    status: str
    project_id: Optional[int] = None
    jira_epic_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectForEpic] = None # Non-recursive project info
    risks: List[Risk] = []

class Project(BaseModel):
    """The full response for a Project, including its epics."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    jira_project_key: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    epics: List[EpicForProject] = [] # Non-recursive epic info

# --- Schemas for Creating New Items ---

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    jira_project_key: Optional[str] = None

class EpicCreate(BaseModel):
    title: str
    description: Optional[str] = None
    target_launch_date: Optional[date] = None
    actual_launch_date: Optional[date] = None
    status: str = "Planned"
    project_id: Optional[int] = None
    jira_epic_key: Optional[str] = None

class RiskCreate(BaseModel):
    description: str
    mitigation_plan: Optional[str] = None
    status: str = "Open"

class RiskUpdateCreate(BaseModel):
    update_text: str

# --- Schemas for Updating Existing Items ---

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    jira_project_key: Optional[str] = None

class EpicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_launch_date: Optional[date] = None
    actual_launch_date: Optional[date] = None
    status: Optional[str] = None
    project_id: Optional[int] = None
    jira_epic_key: Optional[str] = None

class RiskUpdate(BaseModel):
    description: Optional[str] = None
    mitigation_plan: Optional[str] = None
    status: Optional[str] = None 