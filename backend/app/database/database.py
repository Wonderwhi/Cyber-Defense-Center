from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()