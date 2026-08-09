from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: str

    # Defaults keep incident intake simple in Swagger while still capturing useful metadata.
    category: str = "General"
    priority: str = "Medium"

    status: str = "Open"

    reported_by: int
    assigned_to: Optional[int] = None

    # Both fields point to user records when they are provided.


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None

    # Analysts can patch either field without resending the full incident payload.
    category: Optional[str] = None
    priority: Optional[str] = None

    status: Optional[str] = None

    reported_by: Optional[int] = None
    assigned_to: Optional[int] = None

    # Partial updates are allowed, so every field stays optional here.


class IncidentResponse(BaseModel):
    id: int

    title: str
    description: str
    severity: str

    # Echo these so dashboards can sort and segment incidents in one response.
    category: str
    priority: str

    status: str

    reported_by: int
    assigned_to: Optional[int] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)