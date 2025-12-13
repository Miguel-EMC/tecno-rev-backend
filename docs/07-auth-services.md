# Authentication Services - Step by Step

This guide shows you how to build the complete authentication business logic including password hashing, JWT tokens, and user management.

## What Are Services?

Services contain:
- **Business logic**: Password hashing, token generation
- **Database operations**: Create, read, update users
- **Authentication**: Verify credentials, validate tokens
- **Dependencies**: Get current user from requests

## Prerequisites

Add these dependencies to `requirements.txt`:

```txt
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

Install them:

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

## Step 1: Create the Service File

Create `app/modules/auth/service.py`:

```bash
touch app/modules/auth/service.py
```

## Step 2: Add Imports

Open `app/modules/auth/service.py` and add all imports:

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.database import get_session
from .models import User
from .schema import RegisterRequest, CreateUser, UpdateUser
```

**Import breakdown:**
- `datetime`, `timedelta`, `timezone`: For token expiration
- `jose.jwt`: For creating/verifying JWT tokens
- `passlib.context`: For password hashing
- `SQLModel`: For database queries
- `FastAPI`: For HTTP exceptions and dependencies
- `OAuth2PasswordBearer`: OAuth2 token scheme

## Step 3: Setup Password Hashing

Add password hashing configuration:

```python
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**What is CryptContext?**
- Uses bcrypt algorithm for hashing
- `deprecated="auto"`: Auto-migrates old hashes if needed
- Industry-standard secure password hashing

### Create Password Hash Function

```python
def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)
```

**How it works:**
```python
plain = "mypassword123"
hashed = get_password_hash(plain)
# Result: "$2b$12$KIXvZ9Qi0..."
```

Each hash is unique (includes random salt).

### Create Password Verify Function

```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

**How it works:**
```python
is_valid = verify_password("mypassword123", user.hashed_password)
# Returns: True or False
```

## Step 4: Setup OAuth2 Scheme

Add OAuth2 password bearer scheme:

```python
# OAuth2 scheme - tokenUrl must match the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
```

**What does this do?**
- Tells FastAPI to expect `Authorization: Bearer <token>` header
- `tokenUrl`: Where clients get tokens (login endpoint)
- Enables "Authorize" button in Swagger docs

## Step 5: Create JWT Token Functions

### Generate Access Token

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

**How it works:**

1. Copy input data (usually `{"sub": "user@email.com"}`)
2. Calculate expiration time
3. Add `exp` (expiration) to payload
4. Encode with SECRET_KEY and algorithm
5. Return JWT string

**Example:**
```python
token = create_access_token(data={"sub": "john@example.com"})
# Result: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Token payload (decoded):
{
  "sub": "john@example.com",
  "exp": 1735123456
}
```

### Decode Access Token

```python
def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

**What it does:**
1. Decode JWT using SECRET_KEY
2. Verify signature is valid
3. Check token hasn't expired
4. Return payload or raise 401 error

## Step 6: Create User Query Functions

### Get User by Email

```python
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    statement = select(User).where(User.email == email, not User.is_deleted)
    return session.exec(statement).first()
```

**Why check `is_deleted`?**
- Implements soft delete
- Deleted users shouldn't be found

### Get User by ID

```python
def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    statement = select(User).where(User.id == user_id, not User.is_deleted)
    return session.exec(statement).first()
```

## Step 7: Create Authentication Function

```python
def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    statement = select(User).where(User.email == email, not User.is_deleted)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user
```

**Authentication flow:**

1. Find user by email
2. Check if user exists → `None` if not
3. Verify password matches → `None` if wrong
4. Check if user is active → `None` if inactive
5. Return user if all checks pass

**Why return None instead of raising exceptions?**
- Prevents information disclosure
- Same response for "user not found" and "wrong password"
- Security best practice

## Step 8: Create User CRUD Functions

### Create User

```python
def create_user(session: Session, user_data: RegisterRequest | CreateUser) -> User:
    """Create a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create user object
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        hashed_password=hashed_password,
        role_id=user_data.role_id,
        branch_id=getattr(user_data, 'branch_id', None),
        is_active=getattr(user_data, 'is_active', True),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

**Step breakdown:**

1. **Check duplicate email**: Prevent duplicate accounts
2. **Hash password**: Never store plain passwords!
3. **Create User object**: Map schema to model
4. **Save to database**: `add()`, `commit()`, `refresh()`
5. **Return created user**: With auto-generated ID

**Why `getattr()`?**
- `RegisterRequest` might not have `is_active`
- Safe way to get attribute with default value

### Update User

```python
def update_user(session: Session, user_id: int, user_data: UpdateUser) -> User:
    """Update an existing user"""
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    update_data = user_data.model_dump(exclude_unset=True)

    # Handle password separately
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

**Key points:**

1. **`exclude_unset=True`**: Only get fields user actually provided
2. **Password handling**: Hash if provided, remove plain password
3. **Dynamic updates**: Loop through provided fields
4. **Database save**: Commit changes

**Example update:**
```python
# User only updates phone
update_data = UpdateUser(phone=9876543210)
# Only phone is in update_data, other fields unchanged
```

## Step 9: Create Current User Dependencies

### Get Current User

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(session, email)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user
```

**Flow:**

1. **Extract token**: From `Authorization: Bearer <token>` header
2. **Decode token**: Get email from `sub` claim
3. **Find user**: By email in database
4. **Check active**: Verify user is active
5. **Return user**: Available in route handlers

**Usage in routes:**
```python
@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

FastAPI automatically:
- Extracts token from header
- Calls `get_current_user()`
- Injects user into route

### Get Current Active User

```python
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
```

**Why separate function?**
- Double-checks user is active
- Can add more checks here (email verified, etc.)
- More semantic name

## Complete Service File

Your complete `app/modules/auth/service.py`:

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.database import get_session
from .models import User
from .schema import RegisterRequest, CreateUser, UpdateUser

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme - tokenUrl must match the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# User authentication
def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    statement = select(User).where(User.email == email, not User.is_deleted)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


# User CRUD operations
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    statement = select(User).where(User.email == email, not User.is_deleted)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    statement = select(User).where(User.id == user_id, not User.is_deleted)
    return session.exec(statement).first()


def create_user(session: Session, user_data: RegisterRequest | CreateUser) -> User:
    """Create a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = get_password_hash(user_data.password)

    # Create user object
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        hashed_password=hashed_password,
        role_id=user_data.role_id,
        branch_id=getattr(user_data, 'branch_id', None),
        is_active=getattr(user_data, 'is_active', True),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user_id: int, user_data: UpdateUser) -> User:
    """Update an existing user"""
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    update_data = user_data.model_dump(exclude_unset=True)

    # Handle password separately
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Dependency for getting current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(session, email)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
```

## Testing Services

Test password hashing:

```python
from app.modules.auth.service import get_password_hash, verify_password

# Hash a password
hashed = get_password_hash("mypassword")
print(hashed)  # $2b$12$...

# Verify password
is_valid = verify_password("mypassword", hashed)
print(is_valid)  # True

is_invalid = verify_password("wrongpassword", hashed)
print(is_invalid)  # False
```

Test JWT token:

```python
from app.modules.auth.service import create_access_token
from jose import jwt

# Create token
token = create_access_token(data={"sub": "test@example.com"})
print(token)

# Decode token
from app.core.config import settings
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
print(payload)  # {'sub': 'test@example.com', 'exp': ...}
```

## Security Best Practices

### 1. Always Hash Passwords

```python
# ✅ Good
hashed = get_password_hash(password)
user.hashed_password = hashed

# ❌ Bad
user.password = password  # Plain text!
```

### 2. Use Timing-Safe Comparison

Bcrypt's `verify()` already does this, preventing timing attacks.

### 3. Set Token Expiration

```python
# ✅ Good
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ❌ Bad
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # Way too long
```

### 4. Check User is Active

```python
# ✅ Good
if not user.is_active:
    return None

# ❌ Bad
# Letting inactive users login
```

### 5. Use Soft Delete

```python
# ✅ Good
where(User.email == email, not User.is_deleted)

# ❌ Bad
where(User.email == email)  # Might find deleted users
```

## Common Issues

### Issue 1: "Could not validate credentials"

**Cause:** Invalid or expired token

**Fix:** Check token is fresh, SECRET_KEY matches

### Issue 2: Password Hash Not Verifying

**Cause:** Password was changed but not hashed

**Fix:** Always use `get_password_hash()` when setting password

### Issue 3: "User not found" After Login

**Cause:** Token has wrong email or user was deleted

**Fix:** Verify token payload has correct `sub`, check `is_deleted`

## What's Next?

Now that you have services, create:

1. **Routes** - API endpoints that use these services
2. **Configuration** - JWT secret key and settings

Continue to [Authentication Routes](./08-auth-routes.md) to build the API endpoints.

## Summary

You created:

✅ Password hashing with bcrypt
✅ JWT token creation and validation
✅ User authentication
✅ User CRUD operations
✅ Current user dependencies

These services provide:
- Secure password storage
- Stateless authentication
- Reusable business logic
- Type-safe database operations
