from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
