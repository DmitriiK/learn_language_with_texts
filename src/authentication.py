import os
import json
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

class UserRole(str, Enum):
    Admin = "Admin"
    Superuser = "Superuser"
    User = "User"
    Guest = "Guest"

def load_users():
    if not os.path.exists(USERS_FILE):
        raise FileNotFoundError(f"Users file not found: {USERS_FILE}")
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

users_db = load_users()
security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    user = users_db.get(username)
    if not user or user.get("password") != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": username, "role": user.get("role", "Guest")}
