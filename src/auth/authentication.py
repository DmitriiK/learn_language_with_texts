import os
import json
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

USERS_FILE = os.path.join(os.path.dirname(__file__), ".users.json")


class UserRole(str, Enum):
    SupeAdmin = "SupeAdmin"
    Admin = "Admin"
    User = "User"
    Guest = "Guest"

class AuthUser(BaseModel):
    username: str
    role: UserRole
    full_name: str = ""
    total_text_length_quota: int = 10000

def load_users():
    if not os.path.exists(USERS_FILE):
        raise FileNotFoundError(f"Users file not found: {USERS_FILE}")
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


users_db = load_users()
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> AuthUser:
    username = credentials.username
    password = credentials.password
    user = users_db.get(username)
    if not user or user.get("password") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    role = user.get("role", "Guest")
    quota = user.get("total_text_length_quota", 10000)
    # Ensure role is a valid UserRole
    try:
        role_enum = UserRole(role)
    except ValueError:
        role_enum = UserRole.Guest
    return AuthUser(username=username,
                    role=role_enum,
                    total_text_length_quota=quota)
