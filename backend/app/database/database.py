from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL

# Create the SQLAlchemy engine for the configured database.
engine = create_engine(DATABASE_URL)

# Create a factory for session objects used by requests.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all declarative ORM models.
Base = declarative_base()


# Ensure the users table exists and has the expected password hash column.
def ensure_user_schema(engine_instance=None):
    engine_to_use = engine_instance or engine
    inspector = inspect(engine_to_use)
    if not inspector.has_table("users"):
        with engine_to_use.begin() as conn:
            conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100) UNIQUE NOT NULL, email VARCHAR(255) UNIQUE NOT NULL, hashed_password VARCHAR(255) NOT NULL)"))
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "hashed_password" not in columns:
        if "password" in columns:
            with engine_to_use.begin() as conn:
                conn.execute(text("ALTER TABLE users RENAME COLUMN password TO hashed_password"))
        else:
            with engine_to_use.begin() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"))


# Ensure incidents table has the reporter link expected by the ORM model.
def ensure_incident_schema(engine_instance=None):
    engine_to_use = engine_instance or engine
    inspector = inspect(engine_to_use)

    if not inspector.has_table("incidents"):
        return

    columns = {column["name"] for column in inspector.get_columns("incidents")}
    if "reported_by" not in columns:
        with engine_to_use.begin() as conn:
            conn.execute(text("ALTER TABLE incidents ADD COLUMN reported_by INTEGER"))

    # Legacy schemas can have updated_at as NOT NULL, but inserts set it later.
    column_meta = {column["name"]: column for column in inspector.get_columns("incidents")}
    updated_at = column_meta.get("updated_at")
    if (
        updated_at is not None
        and updated_at.get("nullable") is False
        and engine_to_use.dialect.name == "postgresql"
    ):
        with engine_to_use.begin() as conn:
            conn.execute(text("ALTER TABLE incidents ALTER COLUMN updated_at DROP NOT NULL"))


# Dependency provider that yields a DB session and closes it after use.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()