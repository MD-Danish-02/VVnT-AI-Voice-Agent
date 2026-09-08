from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    lead_id: UUID
    scheduled_at: datetime
    status: str = "scheduled"
    meeting_details: Optional[str] = None


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    meeting_details: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lead_id: UUID
    scheduled_at: datetime
    status: str
    meeting_details: Optional[str] = None
    created_at: datetime
    updated_at: datetime
