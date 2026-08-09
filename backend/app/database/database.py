from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Shared SQLAlchemy engine for the whole app.
engine = create_engine(DATABASE_URL)

# Request handlers pull database sessions from this factory.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Every ORM model inherits from this base.
Base = declarative_base()


# Ensure the users table exists and has the expected password hash column.
def ensure_user_schema(engine_instance: Engine | None = None) -> None:
    engine_to_use = engine_instance or engine
    inspector = inspect(engine_to_use)

    if not inspector.has_table("users"):
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        hashed_password VARCHAR(255) NOT NULL
                    )
                    """
                )
            )
        return

    columns = {column["name"] for column in inspector.get_columns("users")}

    if "hashed_password" not in columns:
        if "password" in columns:
            with engine_to_use.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE users RENAME COLUMN password TO hashed_password"
                    )
                )
        else:
            with engine_to_use.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"
                    )
                )


# Ensure the incidents table matches the ORM model.
def ensure_incident_schema(engine_instance: Engine | None = None) -> None:
    engine_to_use = engine_instance or engine
    inspector = inspect(engine_to_use)

    if not inspector.has_table("incidents"):
        return

    columns = {column["name"] for column in inspector.get_columns("incidents")}

    # Keep the link to the user who originally reported the incident.
    if "reported_by" not in columns:
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE incidents ADD COLUMN reported_by INTEGER"
                )
            )

    # Add the analyst assignment column used during triage and investigation.
    if "assigned_to" not in columns:
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE incidents ADD COLUMN assigned_to INTEGER"
                )
            )

    # Category supports filtering and dashboard groupings (phishing, malware, etc.).
    if "category" not in columns:
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE incidents ADD COLUMN category VARCHAR(100) DEFAULT 'General'"
                )
            )

    # Priority lets analysts rank response order independent of severity.
    if "priority" not in columns:
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE incidents ADD COLUMN priority VARCHAR(50) DEFAULT 'Medium'"
                )
            )

    # Legacy schemas can have updated_at as NOT NULL.
    column_meta = {
        column["name"]: column
        for column in inspector.get_columns("incidents")
    }

    updated_at = column_meta.get("updated_at")

    if (
        updated_at is not None
        and updated_at.get("nullable") is False
        and engine_to_use.dialect.name == "postgresql"
    ):
        with engine_to_use.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE incidents ALTER COLUMN updated_at DROP NOT NULL"
                )
            )


# FastAPI dependency that provides one database session per request.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()