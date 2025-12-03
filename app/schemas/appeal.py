from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AppealCreate(BaseModel):
    lead_external_id: str
    source_id: int
    message: Optional[str] = None
    lead_name: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_email: Optional[str] = None


class AppealResponse(BaseModel):
    appeal_id: int
    lead_id: int
    lead_external_id: str
    source_id: int
    source_name: str
    operator: Optional[dict] = None
    status: str
    created_at: datetime


class LeadResponse(BaseModel):
    id: int
    external_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    appeals_count: int


class LeadAppealResponse(BaseModel):
    id: int
    source: str
    operator: Optional[str] = None
    status: str
    created_at: datetime
