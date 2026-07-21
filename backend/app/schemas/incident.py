from pydantic import BaseModel
from datetime import datetime


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str
    reported_by: int
    # reported_by must be an existing user ID from the users table.


class IncidentUpdate(BaseModel):
    title: str
    description: str
    severity: str
    status: str
    reported_by: int
    # The update payload can also change the incident owner if needed.


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    status: str
    reported_by: int
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True