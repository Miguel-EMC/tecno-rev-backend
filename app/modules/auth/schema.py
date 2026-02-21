from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Union
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
    phone: str = Field(
        min_length=10, description="Phone number with country code, e.g., +54999763190"
    )
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
    phone: str
    role_id: int
    branch_id: int | None = None
    is_active: bool = True


class UpdateUser(BaseModel):
    """Schema for updating an existing user"""

    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
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
    phone: Union[str, int]
    is_active: bool
    role_id: int
    branch_id: int | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("phone", mode="before")
    @classmethod
    def phone_to_str(cls, v):
        if isinstance(v, (int, float)):
            return str(v)
        return v

    class Config:
        from_attributes = True


# User Information Schemas
class UserInformationBase(BaseModel):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class UserInformationCreate(UserInformationBase):
    pass


class UserInformationUpdate(UserInformationBase):
    pass


class UserInformationResponse(UserInformationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
