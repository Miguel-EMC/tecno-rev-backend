# Authentication Routes - Step by Step

This guide shows you how to create all the API endpoints for user registration, login, and profile management.

## What Are Routes?

Routes (or endpoints) are:
- **HTTP endpoints**: URLs that clients can call
- **Request handlers**: Process HTTP requests
- **Response senders**: Return JSON data to clients
- **Entry points**: Where users interact with your API

## Prerequisites

Make sure you have completed:
- [Authentication Schemas](./06-auth-schemas.md)
- [Authentication Services](./07-auth-services.md)

Add this dependency:

```txt
python-multipart==0.0.12
```

Required for OAuth2 form data:

```bash
pip install python-multipart
```

## Step 1: Create the Router File

Create `app/modules/auth/router.py`:

```bash
touch app/modules/auth/router.py
```

## Step 2: Add Imports

Open `app/modules/auth/router.py` and add:

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from .schema import RegisterRequest, UpdateUser, UserResponse, TokenResponse
from .service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user,
    get_current_active_user,
)
from .models import User
```

**Import breakdown:**
- `APIRouter`: Creates a group of related routes
- `Depends`: Dependency injection
- `OAuth2PasswordRequestForm`: Standard OAuth2 login form
- `Session`: Database session
- Schemas, services, and models from your modules

## Step 3: Create the Router

Add the API router:

```python
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
```

**Parameters:**
- `prefix="/api/auth"`: All routes start with `/api/auth`
- `tags=["Authentication"]`: Groups routes in API docs

**Result:**
- Route `/register` becomes `/api/auth/register`
- Route `/token` becomes `/api/auth/token`
- All routes grouped under "Authentication" in docs

## Step 4: Create Register Endpoint

Add user registration endpoint:

```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """Register a new user"""
    user = create_user(session, user_data)
    return user
```

**Breakdown:**

| Part | Explanation |
|------|-------------|
| `@router.post("/register")` | POST request to `/api/auth/register` |
| `response_model=UserResponse` | Response follows UserResponse schema |
| `status_code=201` | Returns 201 Created on success |
| `user_data: RegisterRequest` | Validates request body |
| `session = Depends(get_session)` | Injects database session |
| `create_user(session, user_data)` | Calls service function |

**Request example:**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": 1234567890,
  "role_id": 5
}
```

**Response example (201 Created):**
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

**Possible errors:**
- `400 Bad Request`: Email already registered
- `422 Validation Error`: Invalid data (password too short, invalid email, etc.)

## Step 5: Create Login Endpoint

Add OAuth2 compatible login endpoint:

```python
@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
```

**Important OAuth2 details:**

1. **`OAuth2PasswordRequestForm`**: Standard OAuth2 form with fields:
   - `username`: The email (OAuth2 calls it username)
   - `password`: The password

2. **Content-Type**: Must be `application/x-www-form-urlencoded`

3. **`WWW-Authenticate: Bearer`**: Tells client to use Bearer token auth

**Request example (Form Data):**
```bash
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=john@example.com&password=password123
```

**Note:** Even though we use email, OAuth2 spec requires field name `username`.

**Response example (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huQGV4YW1wbGUuY29tIiwiZXhwIjoxNzM1MTIzNDU2fQ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Possible errors:**
- `401 Unauthorized`: Wrong email or password, or inactive user

## Step 6: Create Get Profile Endpoint

Add endpoint to get current user profile:

```python
@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user profile"""
    return current_user
```

**How authentication works here:**

1. Client sends request with token:
   ```
   GET /api/auth/profile
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

2. `Depends(get_current_active_user)`:
   - Extracts token from Authorization header
   - Validates token
   - Gets user from database
   - Injects user into `current_user` parameter

3. Route simply returns the user

**Request example:**
```bash
GET /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response example (200 OK):**
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

**Possible errors:**
- `401 Unauthorized`: Missing, invalid, or expired token
- `403 Forbidden`: User is inactive

## Step 7: Create Update Profile Endpoint

Add endpoint to update current user profile:

```python
@router.patch("/profile", response_model=UserResponse)
def update_profile(
    user_data: UpdateUser,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update current authenticated user profile"""
    updated_user = update_user(session, current_user.id, user_data)
    return updated_user
```

**Key points:**

1. **`PATCH` method**: For partial updates
2. **Authentication required**: Uses `get_current_active_user`
3. **Updates own profile**: Uses `current_user.id`
4. **Partial updates**: Only provided fields are updated

**Request example:**
```bash
PATCH /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "first_name": "Jonathan",
  "phone": 9876543210
}
```

**Response example (200 OK):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "first_name": "Jonathan",
  "last_name": "Doe",
  "phone": 9876543210,
  "is_active": true,
  "role_id": 5,
  "branch_id": null,
  "created_at": "2025-12-13T10:00:00Z",
  "updated_at": "2025-12-13T11:30:00Z"
}
```

**Possible errors:**
- `401 Unauthorized`: Invalid token
- `403 Forbidden`: User is inactive
- `422 Validation Error`: Invalid data

## Complete Router File

Your complete `app/modules/auth/router.py`:

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from .schema import RegisterRequest, UpdateUser, UserResponse, TokenResponse
from .service import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user,
    get_current_active_user,
)
from .models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    """Register a new user"""
    user = create_user(session, user_data)
    return user


@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user profile"""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_profile(
    user_data: UpdateUser,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update current authenticated user profile"""
    updated_user = update_user(session, current_user.id, user_data)
    return updated_user
```

## Step 8: Register Router in Main App

Open `app/main.py` and add:

```python
from fastapi import FastAPI
from app.modules.auth.router import router as auth_router

app = FastAPI(
    title="Tecno Rev API",
    description="API for Tecno Rev e-commerce platform",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Tecno Rev API", "status": "running"}
```

**What `include_router()` does:**
- Registers all routes from `auth_router`
- Routes become available at their full paths
- Groups appear in API documentation

## Step 9: Test with FastAPI Docs

Start the server:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI:
```
http://localhost:8000/docs
```

You'll see:

### Authentication Section

1. **POST /api/auth/register**
   - Try it out
   - Fill in user data
   - Execute
   - See 201 Created response

2. **POST /api/auth/token**
   - Try it out
   - Enter email as `username`
   - Enter password
   - Execute
   - Copy the `access_token`

3. **Authorize** (button at top right)
   - Click Authorize
   - Paste token in Value field
   - Click Authorize
   - Now you're authenticated!

4. **GET /api/auth/profile**
   - Try it out (token automatically included)
   - Execute
   - See your user data

5. **PATCH /api/auth/profile**
   - Try it out
   - Update some fields
   - Execute
   - See updated user data

## API Documentation

FastAPI auto-generates docs from your code:

**From route decorators:**
```python
@router.post("/register", response_model=UserResponse, status_code=201)
```

Generates:
- Endpoint path: `POST /api/auth/register`
- Response schema: `UserResponse`
- Success status: `201 Created`

**From docstrings:**
```python
def register(...):
    """Register a new user"""
```

Becomes the endpoint description in docs.

**From schemas:**
```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
```

Generates:
- Request body structure
- Field validations
- Example values

## HTTP Status Codes

Use appropriate status codes:

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Invalid input, business rule violation |
| 401 | Unauthorized | Missing or invalid auth credentials |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error (auto by FastAPI) |
| 500 | Internal Server Error | Unexpected error |

**Examples:**

```python
# 201 Created for registration
@router.post("/register", status_code=status.HTTP_201_CREATED)

# 401 for wrong credentials
raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

# 403 for inactive user
raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Incorrect email or password"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "password"],
      "msg": "String should have at least 8 characters",
      "input": "short"
    }
  ]
}
```

## Dependency Injection

FastAPI's `Depends()` provides clean code:

```python
def get_profile(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    # current_user and session are automatically injected
    pass
```

**How it works:**

1. FastAPI sees `Depends(get_current_active_user)`
2. Calls `get_current_active_user()`
3. That function calls `Depends(oauth2_scheme)` and `Depends(get_session)`
4. FastAPI resolves all dependencies
5. Injects values into your function

**Benefits:**
- Clean, readable code
- Reusable dependencies
- Automatic error handling
- Type safety

## Protected vs Public Routes

**Public routes** (no authentication):
```python
@router.post("/register")
def register(user_data: RegisterRequest):
    # Anyone can register
    pass
```

**Protected routes** (authentication required):
```python
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_active_user)):
    # Must be authenticated
    pass
```

**Admin-only routes** (future):
```python
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user)  # Check role
):
    # Only admins can delete users
    pass
```

## Best Practices

### 1. Use Descriptive Endpoint Names

```python
# ✅ Good
@router.post("/register")
@router.post("/token")
@router.get("/profile")

# ❌ Bad
@router.post("/create")
@router.post("/auth")
@router.get("/user")
```

### 2. Use Appropriate HTTP Methods

| Method | Purpose | Has Body? |
|--------|---------|-----------|
| GET | Retrieve data | No |
| POST | Create resource | Yes |
| PUT | Replace resource | Yes |
| PATCH | Update resource | Yes |
| DELETE | Delete resource | No |

### 3. Use Response Models

```python
# ✅ Good
@router.get("/profile", response_model=UserResponse)

# ❌ Bad
@router.get("/profile")  # Returns raw SQLModel with password!
```

### 4. Add Docstrings

```python
# ✅ Good
def register(...):
    """Register a new user account"""

# ❌ Bad
def register(...):
    pass  # No description in docs
```

### 5. Return Appropriate Status Codes

```python
# ✅ Good
@router.post("/register", status_code=status.HTTP_201_CREATED)

# ❌ Bad
@router.post("/register")  # Returns 200 instead of 201
```

### 6. Use Meaningful Error Messages

```python
# ✅ Good
raise HTTPException(
    status_code=400,
    detail="Email already registered"
)

# ❌ Bad
raise HTTPException(
    status_code=400,
    detail="Error"  # Not helpful!
)
```

## Testing with cURL

Register user:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "phone": 1234567890,
    "role_id": 5
  }'
```

Login:
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

Get profile:
```bash
TOKEN="your-token-here"

curl -X GET "http://localhost:8000/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN"
```

Update profile:
```bash
curl -X PATCH "http://localhost:8000/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated Name"
  }'
```

## What's Next?

Continue to [Authentication Examples](./09-auth-examples.md) for complete usage examples with Python, cURL, and JavaScript.

## Summary

You created 4 API endpoints:

✅ `POST /api/auth/register` - User registration
✅ `POST /api/auth/token` - OAuth2 login
✅ `GET /api/auth/profile` - Get current user
✅ `PATCH /api/auth/profile` - Update profile

These endpoints provide:
- Standard OAuth2 authentication
- Automatic validation
- Interactive API documentation
- Type-safe request/response handling
- Clean dependency injection
