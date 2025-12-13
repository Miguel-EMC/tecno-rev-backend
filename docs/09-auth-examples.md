# Authentication Examples - Complete Usage Guide

This guide provides complete, working examples of how to use the authentication API with different tools and programming languages.

## Prerequisites

Make sure the server is running:

```bash
uvicorn app.main:app --reload
```

Server will be available at: `http://localhost:8000`

## Example 1: Complete Flow with Python

Full registration, login, and profile management:

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

# ========================================
# 1. REGISTER A NEW USER
# ========================================
print("=" * 50)
print("STEP 1: Register a new user")
print("=" * 50)

register_data = {
    "email": "alice@example.com",
    "password": "securepass123",
    "first_name": "Alice",
    "last_name": "Smith",
    "phone": 5551234567,
    "role_id": 5  # CUSTOMER role
}

response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)

if response.status_code == 201:
    user = response.json()
    print(f"✅ User registered successfully!")
    print(f"   ID: {user['id']}")
    print(f"   Email: {user['email']}")
    print(f"   Name: {user['first_name']} {user['last_name']}")
else:
    print(f"❌ Registration failed: {response.json()}")
    exit(1)

# ========================================
# 2. LOGIN TO GET ACCESS TOKEN
# ========================================
print("\n" + "=" * 50)
print("STEP 2: Login to get access token")
print("=" * 50)

login_data = {
    "email": "alice@example.com",
    "password": "securepass123"
}

response = requests.post(f"{BASE_URL}/api/auth/token", json=login_data)

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data["access_token"]
    expires_in = token_data["expires_in"]

    print(f"✅ Login successful!")
    print(f"   Token: {access_token[:50]}...")
    print(f"   Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
else:
    print(f"❌ Login failed: {response.json()}")
    exit(1)

# ========================================
# 3. GET USER PROFILE
# ========================================
print("\n" + "=" * 50)
print("STEP 3: Get user profile")
print("=" * 50)

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers)

if response.status_code == 200:
    profile = response.json()
    print(f"✅ Profile retrieved!")
    print(f"   ID: {profile['id']}")
    print(f"   Email: {profile['email']}")
    print(f"   Name: {profile['first_name']} {profile['last_name']}")
    print(f"   Phone: {profile['phone']}")
    print(f"   Active: {profile['is_active']}")
    print(f"   Role ID: {profile['role_id']}")
else:
    print(f"❌ Failed to get profile: {response.json()}")

# ========================================
# 4. UPDATE USER PROFILE
# ========================================
print("\n" + "=" * 50)
print("STEP 4: Update user profile")
print("=" * 50)

update_data = {
    "first_name": "Alicia",
    "phone": 5559876543
}

response = requests.patch(
    f"{BASE_URL}/api/auth/profile",
    json=update_data,
    headers=headers
)

if response.status_code == 200:
    updated_profile = response.json()
    print(f"✅ Profile updated!")
    print(f"   New name: {updated_profile['first_name']} {updated_profile['last_name']}")
    print(f"   New phone: {updated_profile['phone']}")
else:
    print(f"❌ Failed to update profile: {response.json()}")

# ========================================
# 5. TEST AUTHENTICATION
# ========================================
print("\n" + "=" * 50)
print("STEP 5: Test without token (should fail)")
print("=" * 50)

response = requests.get(f"{BASE_URL}/api/auth/profile")  # No headers

if response.status_code == 401:
    print(f"✅ Correctly rejected unauthenticated request")
    print(f"   Error: {response.json()['detail']}")
else:
    print(f"⚠️  Unexpected response: {response.status_code}")

print("\n" + "=" * 50)
print("COMPLETE! All authentication flows work correctly.")
print("=" * 50)
```

**Output:**
```
==================================================
STEP 1: Register a new user
==================================================
✅ User registered successfully!
   ID: 1
   Email: alice@example.com
   Name: Alice Smith

==================================================
STEP 2: Login to get access token
==================================================
✅ Login successful!
   Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWI...
   Expires in: 86400 seconds (24 hours)

==================================================
STEP 3: Get user profile
==================================================
✅ Profile retrieved!
   ID: 1
   Email: alice@example.com
   Name: Alice Smith
   Phone: 5551234567
   Active: True
   Role ID: 5

==================================================
STEP 4: Update user profile
==================================================
✅ Profile updated!
   New name: Alicia Smith
   New phone: 5559876543

==================================================
STEP 5: Test without token (should fail)
==================================================
✅ Correctly rejected unauthenticated request
   Error: Not authenticated

==================================================
COMPLETE! All authentication flows work correctly.
==================================================
```

## Example 2: Using with cURL

### Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "password123",
    "first_name": "Bob",
    "last_name": "Johnson",
    "phone": 5551112222,
    "role_id": 5
  }' | json_pp
```

**Response:**
```json
{
  "id": 2,
  "email": "bob@example.com",
  "first_name": "Bob",
  "last_name": "Johnson",
  "phone": 5551112222,
  "is_active": true,
  "role_id": 5,
  "branch_id": null,
  "created_at": "2025-12-13T10:00:00Z",
  "updated_at": "2025-12-13T10:00:00Z"
}
```

### Login and Save Token

```bash
# Login and extract token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"password123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

### Get Profile with Token

```bash
curl -X GET "http://localhost:8000/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN" | json_pp
```

**Response:**
```json
{
  "id": 2,
  "email": "bob@example.com",
  "first_name": "Bob",
  "last_name": "Johnson",
  "phone": 5551112222,
  "is_active": true,
  "role_id": 5,
  "branch_id": null,
  "created_at": "2025-12-13T10:00:00Z",
  "updated_at": "2025-12-13T10:00:00Z"
}
```

### Update Profile

```bash
curl -X PATCH "http://localhost:8000/api/auth/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Robert",
    "phone": 5559998888
  }' | json_pp
```

## Example 3: JavaScript/Fetch API

For frontend applications:

```javascript
const BASE_URL = "http://localhost:8000";
let accessToken = null;

// ========================================
// 1. Register User
// ========================================
async function registerUser() {
  const response = await fetch(`${BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: "charlie@example.com",
      password: "mypassword123",
      first_name: "Charlie",
      last_name: "Brown",
      phone: 5553334444,
      role_id: 5
    })
  });

  if (response.ok) {
    const user = await response.json();
    console.log('✅ Registered:', user);
    return user;
  } else {
    const error = await response.json();
    console.error('❌ Registration failed:', error);
    throw error;
  }
}

// ========================================
// 2. Login
// ========================================
async function login(email, password) {
  const response = await fetch(`${BASE_URL}/api/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email,
      password: password
    })
  });

  if (response.ok) {
    const data = await response.json();
    accessToken = data.access_token;
    console.log('✅ Logged in. Token:', accessToken.substring(0, 20) + '...');

    // Store token in localStorage
    localStorage.setItem('access_token', accessToken);

    return data;
  } else {
    const error = await response.json();
    console.error('❌ Login failed:', error);
    throw error;
  }
}

// ========================================
// 3. Get Profile
// ========================================
async function getProfile() {
  const token = accessToken || localStorage.getItem('access_token');

  const response = await fetch(`${BASE_URL}/api/auth/profile`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (response.ok) {
    const profile = await response.json();
    console.log('✅ Profile:', profile);
    return profile;
  } else {
    const error = await response.json();
    console.error('❌ Failed to get profile:', error);
    throw error;
  }
}

// ========================================
// 4. Update Profile
// ========================================
async function updateProfile(updates) {
  const token = accessToken || localStorage.getItem('access_token');

  const response = await fetch(`${BASE_URL}/api/auth/profile`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updates)
  });

  if (response.ok) {
    const profile = await response.json();
    console.log('✅ Profile updated:', profile);
    return profile;
  } else {
    const error = await response.json();
    console.error('❌ Failed to update profile:', error);
    throw error;
  }
}

// ========================================
// 5. Logout
// ========================================
function logout() {
  accessToken = null;
  localStorage.removeItem('access_token');
  console.log('✅ Logged out');
}

// ========================================
// Usage Example
// ========================================
async function runExample() {
  try {
    // Register
    await registerUser();

    // Login
    await login("charlie@example.com", "mypassword123");

    // Get profile
    await getProfile();

    // Update profile
    await updateProfile({
      first_name: "Charles",
      phone: 5557778888
    });

    // Get updated profile
    await getProfile();

    // Logout
    logout();

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the example
runExample();
```

## Example 4: Using Axios (React/Vue)

For modern frontend frameworks:

```javascript
import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add token
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ========================================
// Authentication Service
// ========================================
export const authService = {
  async register(userData) {
    const response = await API.post('/api/auth/register', userData);
    return response.data;
  },

  async login(email, password) {
    const response = await API.post('/api/auth/token', {
      email: email,
      password: password
    });

    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);

    return response.data;
  },

  async getProfile() {
    const response = await API.get('/api/auth/profile');
    return response.data;
  },

  async updateProfile(updates) {
    const response = await API.patch('/api/auth/profile', updates);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};

// ========================================
// Usage in React Component
// ========================================
import React, { useState, useEffect } from 'react';
import { authService } from './authService';

function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadProfile() {
      try {
        const data = await authService.getProfile();
        setProfile(data);
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      const updated = await authService.updateProfile({
        first_name: e.target.firstName.value,
        phone: parseInt(e.target.phone.value)
      });
      setProfile(updated);
      alert('Profile updated!');
    } catch (error) {
      alert('Failed to update profile');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Profile</h1>
      <p>Email: {profile.email}</p>
      <p>Name: {profile.first_name} {profile.last_name}</p>

      <form onSubmit={handleUpdate}>
        <input name="firstName" defaultValue={profile.first_name} />
        <input name="phone" type="number" defaultValue={profile.phone} />
        <button type="submit">Update</button>
      </form>
    </div>
  );
}
```

## Example 5: Error Handling

Proper error handling:

```python
import requests

BASE_URL = "http://localhost:8000"

def register_user(user_data):
    """Register with error handling"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        response.raise_for_status()  # Raises HTTPError for bad status

        return response.json()

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_detail = e.response.json().get('detail', 'Unknown error')

        if status_code == 400:
            print(f"❌ Registration failed: {error_detail}")
            # Email already exists
        elif status_code == 422:
            print(f"❌ Validation error:")
            for error in error_detail:
                field = ' -> '.join(str(x) for x in error['loc'])
                msg = error['msg']
                print(f"   {field}: {msg}")
        else:
            print(f"❌ Unexpected error ({status_code}): {error_detail}")

        return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def login(email, password):
    """Login with error handling"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/token",
            json={"email": email, "password": password}
        )
        response.raise_for_status()

        token_data = response.json()
        print(f"✅ Login successful!")
        return token_data['access_token']

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Invalid email or password")
        else:
            print(f"❌ Login failed: {e.response.json()['detail']}")
        return None

def get_profile(token):
    """Get profile with error handling"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code

        if status_code == 401:
            print("❌ Invalid or expired token")
        elif status_code == 403:
            print("❌ User account is inactive")
        else:
            print(f"❌ Error: {e.response.json()['detail']}")

        return None

# Usage
user_data = {
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "phone": 1234567890,
    "role_id": 5
}

user = register_user(user_data)
if user:
    token = login(user_data['email'], user_data['password'])
    if token:
        profile = get_profile(token)
        if profile:
            print(f"Welcome, {profile['first_name']}!")
```

## Example 6: Token Expiration Handling

Handle token expiration gracefully:

```python
import requests
from datetime import datetime, timedelta

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None
        self.token_expires_at = None
        self.email = None
        self.password = None

    def login(self, email, password):
        """Login and store credentials"""
        response = requests.post(
            f"{self.base_url}/api/auth/token",
            json={"email": email, "password": password}
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
            self.email = email
            self.password = password
            print(f"✅ Logged in. Token expires at {self.token_expires_at}")
            return True
        else:
            print(f"❌ Login failed: {response.json()}")
            return False

    def _is_token_expired(self):
        """Check if token is expired or about to expire"""
        if not self.token_expires_at:
            return True

        # Consider expired if less than 5 minutes remaining
        return datetime.now() >= (self.token_expires_at - timedelta(minutes=5))

    def _refresh_token(self):
        """Re-login to get new token"""
        print("⚠️  Token expired, refreshing...")
        return self.login(self.email, self.password)

    def _get_headers(self):
        """Get headers with valid token"""
        if self._is_token_expired():
            if not self._refresh_token():
                raise Exception("Failed to refresh token")

        return {"Authorization": f"Bearer {self.access_token}"}

    def get_profile(self):
        """Get profile with automatic token refresh"""
        response = requests.get(
            f"{self.base_url}/api/auth/profile",
            headers=self._get_headers()
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get profile: {response.json()}")
            return None

# Usage
client = APIClient("http://localhost:8000")

if client.login("user@example.com", "password123"):
    # Will automatically refresh token if needed
    profile = client.get_profile()
    print(f"Name: {profile['first_name']} {profile['last_name']}")
```

## Summary

You now have complete examples for:

✅ **Python** - Full authentication flow with requests
✅ **cURL** - Command-line testing
✅ **JavaScript** - Frontend integration with Fetch API
✅ **Axios** - React/Vue integration
✅ **Error handling** - Proper error management
✅ **Token expiration** - Automatic token refresh

Use these examples as templates for your own applications!

## Next Steps

- Implement refresh tokens for better security
- Add email verification
- Implement password reset
- Add social login (Google, GitHub, etc.)
- Implement rate limiting

## Troubleshooting

### "Not authenticated" error

**Problem:** Getting 401 errors

**Solutions:**
1. Check token is included in `Authorization` header
2. Verify token format: `Bearer <token>` (with space)
3. Check token hasn't expired
4. Verify SECRET_KEY matches between login and validation

### "Email already registered"

**Problem:** Can't register duplicate email

**Solutions:**
1. Use different email
2. Or delete existing user from database
3. Or implement email verification + resend

### CORS errors in browser

**Problem:** Browser blocks requests

**Solution:** Add CORS middleware in `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
