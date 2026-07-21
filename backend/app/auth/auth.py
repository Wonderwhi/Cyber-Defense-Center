from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

# NOTE: Replace this value with a strong secret key in production.
SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Shared password-hashing context for the auth flow.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Convert a plain text password into a bcrypt hash.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify a submitted password against the stored hash.
def verify_password(plain_password: str, hashed_password: Any) -> bool:
    return pwd_context.verify(plain_password, str(hashed_password))


# Generate a signed JWT containing the user identity payload.
def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)