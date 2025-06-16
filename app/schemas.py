from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# Epic schemas
class EpicBase(BaseModel):
    title: str
    description: Optional[str] = None
    target_launch_date: Optional[date] = None
    actual_launch_date: Optional[date] = None
    status: str = "Planned"

class EpicCreate(EpicBase):
    pass

class EpicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_launch_date: Optional[date] = None
    actual_launch_date: Optional[date] = None
    status: Optional[str] = None

class Risk(BaseModel):
    id: int
    epic_id: int
    description: str
    mitigation_plan: Optional[str] = None
    date_added: date
    status: str
    created_at: datetime
    updated_at: datetime
    updates: List["RiskUpdateResponse"] = []

    class Config:
        from_attributes = True

class Epic(EpicBase):
    id: int
    created_at: datetime
    updated_at: datetime
    risks: List[Risk] = []

    class Config:
        from_attributes = True

# Risk schemas
class RiskBase(BaseModel):
    description: str
    mitigation_plan: Optional[str] = None
    status: str = "Open"

class RiskCreate(RiskBase):
    pass

class RiskUpdate(BaseModel):
    description: Optional[str] = None
    mitigation_plan: Optional[str] = None
    status: Optional[str] = None

# Risk Update schemas
class RiskUpdateBase(BaseModel):
    update_text: str

class RiskUpdateCreate(RiskUpdateBase):
    pass

class RiskUpdateResponse(RiskUpdateBase):
    id: int
    risk_id: int
    date_added: date
    created_at: datetime

    class Config:
        from_attributes = True

# Update forward references
Risk.model_rebuild() 