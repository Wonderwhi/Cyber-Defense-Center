import unittest
from sqlalchemy import create_engine, inspect, text

from app.database.database import ensure_user_schema


class EnsureUserSchemaTests(unittest.TestCase):
    def test_ensure_user_schema_adds_missing_password_column(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as conn:
                conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), email VARCHAR(255))"))

            ensure_user_schema(engine)

            inspector = inspect(engine)
            columns = {column["name"] for column in inspector.get_columns("users")}
            self.assertIn("password", columns)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
