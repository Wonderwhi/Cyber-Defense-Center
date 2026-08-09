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

# These imports make sure SQLAlchemy sees both tables before startup.
_ = (User, Incident)

# Create all database tables defined by the SQLAlchemy models.
Base.metadata.create_all(bind=engine)

# Patch older local databases so the app can still boot cleanly.
ensure_user_schema(engine)
ensure_incident_schema(engine)

app = FastAPI(
    title="Cyber Defense Center",
    description="A cybersecurity platform for monitoring security events, vulnerabilities, incidents, and threat intelligence.",
    version="1.0.0",
)

# Wire the user and incident endpoints into the app.
app.include_router(users_router)
app.include_router(
    incidents_router,
    prefix="/incidents",
    tags=["Incidents"],
)


@app.get("/")
def root():
    return {
        "application": "Cyber Defense Center",
        "status": "Running",
        "version": "1.0.0",
    }