import os

from dotenv import load_dotenv

# Load environment variables from the .env file into the application.
load_dotenv()

# Database connection string used by SQLAlchemy.
DATABASE_URL = os.getenv("DATABASE_URL")