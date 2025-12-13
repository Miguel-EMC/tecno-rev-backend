# Authentication Schemas - Step by Step

This guide shows you how to create all the request and response schemas for the authentication system using Pydantic.

## What Are Schemas?

Schemas define:
- **Request validation**: What data the API accepts
- **Response format**: How data is returned to clients
- **Type safety**: Automatic validation and type checking
- **API documentation**: Auto-generated docs in Swagger/ReDoc

## Prerequisites

Make sure you have these dependencies in `requirements.txt`:

```txt
fastapi[standard]==0.124.0
pydantic==2.8.0
email-validator==2.2.0
```

Install email-validator for email validation:

```bash
pip install email-validator
```

## Step 1: Create the Schemas File

Create the file `app/modules/auth/schema.py`:

```bash
touch app/modules/auth/schema.py
```

## Step 2: Add Base Imports

Open `app/modules/auth/schema.py` and add:

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
```

**What each import does:**
- `BaseModel`: Base class for all Pydantic models
- `EmailStr`: Special type that validates email format
- `Field`: Add validation rules and metadata
- `Optional`: For fields that can be None
- `datetime`: For timestamp fields

## Step 3: Create RegisterRequest Schema

Add the registration schema:

```python
class RegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    phone: int
    role_id: int = Field(default=5, description="Default role is CUSTOMER")
    branch_id: Optional[int] = None
```

**Field breakdown:**

| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `email` | `EmailStr` | Valid email format | User's email (used for login) |
| `password` | `str` | Minimum 8 characters | Plain password (will be hashed) |
| `first_name` | `str` | 2-100 characters | User's first name |
| `last_name` | `str` | 2-100 characters | User's last name |
| `phone` | `int` | Integer | Phone number |
| `role_id` | `int` | Defaults to 5 | User role (5 = CUSTOMER) |
| `branch_id` | `Optional[int]` | Can be None | Optional branch assignment |

**Why these validations?**
- `min_length=8` on password: Security best practice
- `EmailStr`: Ensures valid email format
- `min_length=2`: Prevents single-letter names
- `max_length=100`: Database constraint matching

**Example valid request:**
```json
{
  "email": "john@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": 1234567890,
  "role_id": 5
}
```

## Step 4: Create TokenResponse Schema

Add the JWT token response schema:

```python
class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

**Field breakdown:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `access_token` | `str` | - | The JWT token string |
| `token_type` | `str` | `"bearer"` | OAuth2 token type (always "bearer") |
| `expires_in` | `int` | - | Token lifetime in seconds |

**Why these fields?**
- `access_token`: The actual JWT that client will use
- `token_type`: OAuth2 standard requires this
- `expires_in`: Client knows when to refresh token

**Example response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

## Step 5: Create UpdateUser Schema

Add the profile update schema:

```python
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
```

**Why all fields are optional?**
- Users can update only the fields they want to change
- `| None = None` means the field is optional
- Pydantic's `exclude_unset=True` will ignore unset fields

**Example partial update:**
```json
{
  "first_name": "Jonathan",
  "phone": 9876543210
}
```

Only `first_name` and `phone` will be updated. Other fields remain unchanged.

## Step 6: Create UserResponse Schema

Add the user data response schema:

```python
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
```

**Important notes:**

1. **NO password field!** Never return passwords in responses
2. **`from_attributes = True`**: Allows Pydantic to read from SQLModel objects
3. **`branch_id` is optional**: Some users may not have a branch

**Example response:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": 1234567890,
  "is_active": true,
  "role_id": 5,
  "branch_id": null,
  "created_at": "2025-12-13T10:00:00Z",
  "updated_at": "2025-12-13T10:00:00Z"
}
```

## Step 7: (Optional) Create Admin User Schema

For admin operations, create a schema with more control:

```python
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
```

**Difference from RegisterRequest:**
- Admin can set any `role_id` (not just CUSTOMER)
- Admin can set `is_active` status
- Used for creating employees, managers, etc.

## Complete File

Your complete `app/modules/auth/schema.py` should look like:

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Authentication Schemas
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
```

## Testing Your Schemas

You can test schemas in Python:

```python
from app.modules.auth.schema import RegisterRequest

# Valid data
data = {
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "phone": 1234567890
}

user = RegisterRequest(**data)
print(user.email)  # test@example.com

# Invalid data - will raise validation error
try:
    invalid = RegisterRequest(
        email="not-an-email",  # Invalid email
        password="short",       # Too short
        first_name="T",        # Too short
        last_name="U",
        phone=123
    )
except Exception as e:
    print(f"Validation error: {e}")
```

## Common Validation Errors

### 1. Invalid Email Format

```python
RegisterRequest(email="notanemail", ...)
```

**Error:**
```
value is not a valid email address
```

### 2. Password Too Short

```python
RegisterRequest(password="short", ...)
```

**Error:**
```
ensure this value has at least 8 characters
```

### 3. Name Too Short

```python
RegisterRequest(first_name="J", ...)
```

**Error:**
```
ensure this value has at least 2 characters
```

## Field Validators (Advanced)

You can add custom validators:

```python
from pydantic import field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    # ... other fields

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has at least one number"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v
```

Now passwords must have at least one digit.

## Best Practices

### 1. Use EmailStr for Email Fields

```python
# ✅ Good
email: EmailStr

# ❌ Bad
email: str  # No validation
```

### 2. Set Minimum Lengths

```python
# ✅ Good
password: str = Field(min_length=8)

# ❌ Bad
password: str  # No minimum
```

### 3. Use Optional Correctly

```python
# ✅ Good - Field can be None
branch_id: Optional[int] = None

# ❌ Bad - Field is required but can be None later
branch_id: Optional[int]
```

### 4. Never Include Passwords in Responses

```python
# ✅ Good
class UserResponse(BaseModel):
    id: int
    email: str
    # No password!

# ❌ Bad
class UserResponse(BaseModel):
    id: int
    email: str
    password: str  # Security risk!
```

### 5. Use Descriptive Docstrings

```python
# ✅ Good
class RegisterRequest(BaseModel):
    """Schema for user registration"""

# ❌ Bad
class RegisterRequest(BaseModel):
    pass  # No description
```

### 6. Match Database Constraints

If your model has `max_length=200`:

```python
# ✅ Good - Matches database
first_name: str = Field(max_length=100)

# ❌ Bad - Mismatch will cause errors
first_name: str  # No limit
```

## What's Next?

Now that you have schemas, you need:

1. **Services** - Business logic for authentication
2. **Routes** - API endpoints that use these schemas
3. **Dependencies** - Get current user from JWT token

Continue to [Authentication Services](./07-auth-services.md) to build the business logic layer.

## Summary

You created 5 schemas:

✅ `RegisterRequest` - User registration with validation
✅ `TokenResponse` - JWT token response
✅ `CreateUser` - Admin user creation
✅ `UpdateUser` - Partial user updates
✅ `UserResponse` - User data response (no password!)

These schemas provide:
- Automatic validation
- Type safety
- API documentation
- Security (no password in responses)
