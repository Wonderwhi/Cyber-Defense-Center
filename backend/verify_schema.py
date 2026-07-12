from sqlalchemy import create_engine, inspect, text
from app.database.database import ensure_user_schema

engine = create_engine('sqlite:///:memory:')
with engine.begin() as conn:
    conn.execute(text('CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), email VARCHAR(255))'))

ensure_user_schema(engine)
inspector = inspect(engine)
cols = {column['name'] for column in inspector.get_columns('users')}
print('password' in cols)
print(cols)
