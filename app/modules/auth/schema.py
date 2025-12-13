from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Authentication Schemas
class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    phone: int
    role_id: int = Field(default=5, description="Default role is CUSTOMER")
    branch_id: Optional[int] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# User CRUD Schemas
class CreateUser(BaseModel):
    """Schema for creating a new user (admin use)"""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: int
    role_id: int
    branch_id: int | None = None
    is_active: bool = True


class UpdateUser(BaseModel):
    """Schema for updating an existing user"""
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: int | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None
    role_id: int | None = None
    branch_id: int | None = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    first_name: str
    last_name: str
    phone: int
    is_active: bool
    role_id: int
    branch_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

