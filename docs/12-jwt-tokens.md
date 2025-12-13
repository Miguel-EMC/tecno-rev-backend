# JWT Tokens - How Authentication Works

## Overview

This application uses **JWT (JSON Web Tokens)** for stateless authentication. This means the server doesn't store session data - all authentication information is contained within the token itself.

## How JWT Works

### 1. Token Generation (Login)

When a user logs in successfully:

```python
# User logs in with email and password
POST /api/auth/token
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

The server:
1. Verifies the email and password
2. Creates a JWT token containing user information
3. Signs the token with a secret key
4. Returns the token to the client

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Token Structure

A JWT token has three parts separated by dots (`.`):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9  .  eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjM5MzQ1Njc4fQ  .  XZApsrPVI79QqUaXStDlYOK8QKmVAADqHv24ivdUjn4
    HEADER (Base64)                          PAYLOAD (Base64)                                                       SIGNATURE
```

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "sub": "user@example.com",  // Subject (user identifier)
  "exp": 1734123456           // Expiration timestamp
}
```

**Signature:**
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

### 3. Token Usage (Authentication)

To access protected routes, include the token in the `Authorization` header:

```bash
GET /api/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The server:
1. Extracts the token from the header
2. Verifies the signature using the SECRET_KEY
3. Checks if the token is expired
4. Extracts user information from the payload
5. Allows or denies access

### 4. Token Storage

**Important:** Tokens are **NOT stored on the server**. This is called **stateless authentication**.

**Client-side storage options:**

| Location          | Security | Persistence | Use Case                    |
|-------------------|----------|-------------|-----------------------------|
| localStorage      | ⚠️ Medium | Permanent   | Web apps (most common)      |
| sessionStorage    | ⚠️ Medium | Session only| Single-session apps         |
| Memory (variable) | ✅ High   | Page reload | Maximum security            |
| httpOnly Cookie   | ✅ High   | Configurable| Best for production         |

**Example - localStorage (Web):**
```javascript
// Save token after login
localStorage.setItem('access_token', token);

// Retrieve token for requests
const token = localStorage.getItem('access_token');

// Remove token on logout
localStorage.removeItem('access_token');
```

**Example - Secure Cookie (Recommended for production):**
```python
# Server sets httpOnly cookie (can't be accessed by JavaScript)
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,  # Prevents XSS attacks
    secure=True,    # HTTPS only
    samesite="lax"  # CSRF protection
)
```

## Token Lifecycle

```
1. User Login
   ↓
2. Server Creates Token (with expiration)
   ↓
3. Client Receives & Stores Token
   ↓
4. Client Sends Token with Each Request
   ↓
5. Server Validates Token
   ↓
6. Token Expires (24 hours by default)
   ↓
7. User Must Re-login
```

## Configuration

**File:** `.env`

```bash
# Secret key for signing tokens (NEVER share this!)
SECRET_KEY=your-super-secret-key-here

# Signing algorithm
ALGORITHM=HS256

# Token expiration in minutes (default: 1440 = 24 hours)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**File:** `app/core/config.py`

```python
class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
```

## Token Creation Code

**File:** `app/modules/auth/service.py`

```python
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration to payload
    to_encode.update({"exp": expire})

    # Create and sign token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt
```

## Token Verification Code

**File:** `app/modules/auth/service.py`

```python
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """Get current user from JWT token"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user email from payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user_by_email(session, email=email)
    if user is None:
        raise credentials_exception

    return user
```

## Security Best Practices

### 1. Keep SECRET_KEY Secret

❌ **NEVER do this:**
```python
SECRET_KEY = "my-secret-key"  # Hardcoded in code
```

✅ **Always do this:**
```python
SECRET_KEY = os.getenv("SECRET_KEY")  # From environment variable
```

### 2. Use Strong SECRET_KEY

Generate a strong secret key:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32
```

**Example output:**
```
kZ8vLJH5fPxN2wQc9tYR3mE6sA4bD7nU1oF0gK8jT5h
```

### 3. Set Appropriate Expiration

```python
# Short-lived tokens (more secure but less convenient)
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes

# Medium-lived tokens (balanced)
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

# Long-lived tokens (less secure but more convenient)
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

### 4. Use HTTPS in Production

```python
# Only allow HTTPS in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        HTTPSRedirectMiddleware
    )
```

### 5. Implement Token Refresh (Future Enhancement)

```python
# Instead of long-lived access tokens, use:
# - Short-lived access token (15 min)
# - Long-lived refresh token (7 days)
# - Refresh endpoint to get new access token
```

## Common Issues

### Issue 1: "Could not validate credentials"

**Causes:**
- Token expired
- Invalid token signature
- Token was tampered with
- Wrong SECRET_KEY in .env

**Solution:**
```python
# Check token expiration
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded['exp'])  # Unix timestamp

# Re-login to get new token
```

### Issue 2: Token works locally but not in production

**Cause:** Different SECRET_KEY in production

**Solution:**
```bash
# Ensure same SECRET_KEY in both environments
# Or use different keys but don't share tokens between envs
```

### Issue 3: "Not authenticated" error

**Cause:** Token not included in request

**Solution:**
```javascript
// Make sure to include Authorization header
fetch('/api/auth/profile', {
  headers: {
    'Authorization': `Bearer ${token}`  // ✅ Correct
    // 'Authorization': token            // ❌ Wrong (missing "Bearer ")
  }
})
```

## Testing Tokens

### Decode Token (Without Verification)

```python
import jwt

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)
```

**Output:**
```python
{
  'sub': 'user@example.com',
  'exp': 1734123456
}
```

### Test Token Manually

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass123"}' \
  | jq -r '.access_token')

# 2. Use token to access protected route
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
```

## Advantages of JWT

✅ **Stateless** - No server-side session storage needed
✅ **Scalable** - Works across multiple servers
✅ **Portable** - Can be used across different domains
✅ **Self-contained** - All info is in the token
✅ **Fast** - No database lookup for every request

## Disadvantages of JWT

❌ **Cannot revoke** - Token is valid until expiration
❌ **Size** - Larger than session IDs
❌ **Security** - If stolen, can be used until expiration

## Future Enhancements

1. **Refresh Tokens**
   - Short-lived access tokens
   - Long-lived refresh tokens
   - Refresh endpoint

2. **Token Blacklist**
   - Store revoked tokens in Redis
   - Check on each request
   - Clean up expired tokens

3. **Device Tracking**
   - Store device info in token
   - Detect suspicious activity
   - Multi-device management

4. **Two-Factor Authentication (2FA)**
   - Require second factor
   - Generate TOTP codes
   - Backup codes

## Related Documentation

- [Authentication Services](07-auth-services.md)
- [Authentication Routes](08-auth-routes.md)
- [Authentication Examples](09-auth-examples.md)

## External Resources

- [JWT.io](https://jwt.io/) - Decode and verify tokens
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT specification
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
