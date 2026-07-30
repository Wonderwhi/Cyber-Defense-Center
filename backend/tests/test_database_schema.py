import unittest
from sqlalchemy import create_engine, inspect, text

from app.database.database import ensure_incident_schema, ensure_user_schema


class EnsureUserSchemaTests(unittest.TestCase):
    def test_ensure_user_schema_adds_missing_hashed_password_column(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), email VARCHAR(255))"))

            ensure_user_schema(engine)

            inspector = inspect(engine)
            columns = {column["name"] for column in inspector.get_columns("users")}
            self.assertIn("hashed_password", columns)
        finally:
            engine.dispose()


class EnsureIncidentSchemaTests(unittest.TestCase):
    def test_ensure_incident_schema_adds_missing_reported_by_column(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE TABLE incidents (id INTEGER PRIMARY KEY, title VARCHAR(255), description VARCHAR(1000), severity VARCHAR(50), status VARCHAR(50))"))

            ensure_incident_schema(engine)

            inspector = inspect(engine)
            columns = {column["name"] for column in inspector.get_columns("incidents")}
            self.assertIn("reported_by", columns)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
