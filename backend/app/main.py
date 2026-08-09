from fastapi import FastAPI

from app.database.database import (
    Base,
    engine,
    ensure_incident_schema,
    ensure_user_schema,
)

from app.models.user import User
from app.models.incident import Incident

from app.routers.users import router as users_router
from app.api.incidents import router as incidents_router
from app.api.dashboard import router as dashboard_router

# SQLAlchemy needs these model imports loaded before create_all() runs.
_ = (User, Incident)

# Create all database tables defined by the SQLAlchemy models.
Base.metadata.create_all(bind=engine)

# Keep local/dev databases compatible with the current codebase.
ensure_user_schema(engine)
ensure_incident_schema(engine)

app = FastAPI(
    title="Cyber Defense Center",
    description="A cybersecurity platform for monitoring security events, vulnerabilities, incidents, and threat intelligence.",
    version="1.0.0",
)

# Users routes handle auth and account operations.
app.include_router(users_router)

# Incident routes are grouped under /incidents for CRUD operations.
app.include_router(
    incidents_router,
    prefix="/incidents",
    tags=["Incidents"],
)

# Dashboard routes expose aggregated incident metrics.
app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"],
)


@app.get("/")
def root():
    return {
        "application": "Cyber Defense Center",
        "status": "Running",
        "version": "1.0.0",
    }