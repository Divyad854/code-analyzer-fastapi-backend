from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
import re

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str):
        if not re.search(r"[A-Z]", value) or not re.search(r"[a-z]", value) or not re.search(r"\d", value):
            raise ValueError("Password must contain uppercase, lowercase, and a number")
        return value

class UserResponse(BaseModel):
#     It allows Pydantic to read values directly from object attributes, including SQLAlchemy ORM objects.
# Without it, Pydantic generally expects dictionary-style input.
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
