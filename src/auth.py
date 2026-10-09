
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(
    os.getenv("AUTH_DATABASE_PATH", str(BASE_DIR / "data" / "auth.db"))
).resolve()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 12

password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE_PATH), timeout=30)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_auth_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL
            )
            """
        )


def validate_auth_configuration():
    if len(JWT_SECRET_KEY) < 32:
        raise RuntimeError(
            "JWT_SECRET_KEY must contain at least 32 characters. "
            "Set a strong random value in your environment."
        )


def create_user(email, password):
    email = email.strip().lower()

    if len(email) > 254 or "@" not in email:
        raise HTTPException(status_code=400, detail="Enter a valid email address.")

    if len(password) < 12 or len(password) > 128:
        raise HTTPException(
            status_code=400,
            detail="Password must contain between 12 and 128 characters."
        )

    password_hash = password_hasher.hash(password)
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (user_id, email, password_hash, role, created_at)
                VALUES (?, ?, ?, 'user', ?)
                """,
                (os.urandom(16).hex(), email, password_hash, created_at)
            )
            user_id = cursor.lastrowid
            row = connection.execute(
                "SELECT user_id, email, role, created_at FROM users WHERE email = ?",
                (email,)
            ).fetchone()

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists."
        )

    return dict(row)


def authenticate_user(email, password):
    email = email.strip().lower()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

    if row is None or not password_hasher.verify(password, row["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    return {
        "user_id": row["user_id"],
        "email": row["email"],
        "role": row["role"]
    }


def create_access_token(user):
    validate_auth_configuration()

    now = datetime.now(timezone.utc)

    payload = {
        "sub": user["user_id"],
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    validate_auth_configuration()

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")

        if not user_id:
            raise jwt.InvalidTokenError("Missing user identifier.")

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    with get_connection() as connection:
        row = connection.execute(
            "SELECT user_id, email, role FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Account no longer exists.")

    return dict(row)


def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return user
