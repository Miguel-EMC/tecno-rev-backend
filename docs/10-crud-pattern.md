# CRUD Pattern with Protected Routes

This guide explains the standard CRUD pattern used across all modules in the application, with protected routes requiring authentication.

## Overview

Every module follows the same 3-file structure:

```
app/modules/<module_name>/
├── models.py     # Already exists - SQLModel database models
├── schema.py     # NEW - Pydantic request/response schemas
├── service.py    # NEW - Business logic and database operations
└── router.py     # NEW - API endpoints with route protection
```

## The CRUD Pattern

### Standard Operations

Every resource (Category, Product, Order, etc.) has these operations:

| Operation | HTTP Method | Route | Authentication |
|-----------|-------------|-------|----------------|
| **List** | GET | `/api/{module}/{resources}` | Public |
| **Get One** | GET | `/api/{module}/{resources}/{id}` | Public |
| **Create** | POST | `/api/{module}/{resources}` | **Protected** |
| **Update** | PATCH | `/api/{module}/{resources}/{id}` | **Protected** |
| **Delete** | DELETE | `/api/{module}/{resources}/{id}` | **Protected** |

**Protected routes** require JWT token in `Authorization: Bearer <token>` header.

## Step-by-Step: Creating a CRUD Module

Let's use **Category** as an example. The same pattern applies to all resources.

### Step 1: Create Schemas (schema.py)

Schemas define request/response formats:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Create Schema - What users send to create
class CategoryCreate(BaseModel):
    """Schema for creating a category"""
    name: str = Field(min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


# Update Schema - What users send to update (all optional)
class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


# Response Schema - What API returns to users
class CategoryResponse(BaseModel):
    """Schema for category response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows reading from SQLModel
```

**Pattern:**
- `{Resource}Create`: Required fields for creation
- `{Resource}Update`: All fields optional (partial updates)
- `{Resource}Response`: What API returns (includes id, timestamps, but NO passwords/secrets)

### Step 2: Create Services (service.py)

Services contain business logic and database operations:

```python
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from .models import Category
from .schema import CategoryCreate, CategoryUpdate


# GET ALL - with pagination
def get_categories(session: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """Get all categories with pagination"""
    statement = select(Category).where(not Category.is_deleted).offset(skip).limit(limit)
    return list(session.exec(statement).all())


# GET ONE - by ID
def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    """Get a category by ID"""
    statement = select(Category).where(Category.id == category_id, not Category.is_deleted)
    return session.exec(statement).first()


# CREATE
def create_category(session: Session, category_data: CategoryCreate) -> Category:
    """Create a new category"""
    # 1. Validate (check duplicates, etc.)
    existing = get_category_by_name(session, category_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists"
        )

    # 2. Create model instance
    category = Category(**category_data.model_dump())

    # 3. Save to database
    session.add(category)
    session.commit()
    session.refresh(category)

    return category


# UPDATE
def update_category(session: Session, category_id: int, category_data: CategoryUpdate) -> Category:
    """Update an existing category"""
    # 1. Get existing resource
    category = get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # 2. Get only provided fields
    update_data = category_data.model_dump(exclude_unset=True)

    # 3. Validate updates (check conflicts, etc.)
    if "name" in update_data:
        existing = get_category_by_name(session, update_data["name"])
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{update_data['name']}' already exists"
            )

    # 4. Apply updates
    for field, value in update_data.items():
        setattr(category, field, value)

    # 5. Save to database
    session.add(category)
    session.commit()
    session.refresh(category)

    return category


# DELETE (Soft Delete)
def delete_category(session: Session, category_id: int) -> dict:
    """Soft delete a category"""
    # 1. Get existing resource
    category = get_category_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # 2. Check if can be deleted (no dependencies)
    statement = select(Product).where(Product.category_id == category_id, not Product.is_deleted)
    products = session.exec(statement).all()
    if products:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. It has {len(products)} active products."
        )

    # 3. Soft delete (set is_deleted flag)
    category.is_deleted = True
    session.add(category)
    session.commit()

    return {"message": "Category deleted successfully"}
```

**Pattern:**
- Always check `not {Model}.is_deleted` in queries
- Use `model_dump(exclude_unset=True)` for updates
- Soft delete by setting `is_deleted = True`
- Validate before saving
- Return the model or a message

### Step 3: Create Routes (router.py)

Routes define API endpoints:

```python
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.auth.service import get_current_active_user
from app.modules.auth.models import User
from .schema import CategoryCreate, CategoryUpdate, CategoryResponse
from .service import (
    get_categories,
    get_category_by_id,
    create_category,
    update_category,
    delete_category
)

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])


# GET ALL - Public route
@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """Get all categories (public)"""
    return get_categories(session, skip, limit)


# GET ONE - Public route
@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific category by ID (public)"""
    category = get_category_by_id(session, category_id)
    if not category:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# CREATE - Protected route (requires authentication)
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(
    category_data: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # 🔒 Protected
):
    """Create a new category (protected - requires authentication)"""
    return create_category(session, category_data)


# UPDATE - Protected route
@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # 🔒 Protected
):
    """Update a category (protected - requires authentication)"""
    return update_category(session, category_id, category_data)


# DELETE - Protected route
@router.delete("/categories/{category_id}", status_code=status.HTTP_200_OK)
def delete_existing_category(
    category_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # 🔒 Protected
):
    """Delete a category (protected - requires authentication)"""
    return delete_category(session, category_id)
```

**Pattern:**
- `response_model`: Automatically converts SQLModel to Pydantic schema
- Public routes: No `current_user` parameter
- **Protected routes**: Add `current_user: User = Depends(get_current_active_user)`
- Use `Query()` for query parameters with validation

### Step 4: Register Router in main.py

Add router to FastAPI app:

```python
from fastapi import FastAPI
from app.modules.auth.router import router as auth_router
from app.modules.catalog.router import router as catalog_router

app = FastAPI(
    title="Tecno Rev API",
    description="API for Tecno Rev e-commerce platform",
    version="1.0.0"
)

# Include routers
app.include_router(auth_router)
app.include_router(catalog_router)  # Add this
```

## Route Protection

### Public Routes (No Authentication)

Used for browsing products, categories, etc.:

```python
@router.get("/products", response_model=List[ProductResponse])
def list_products(
    session: Session = Depends(get_session)  # No current_user
):
    """Anyone can view products"""
    return get_products(session)
```

### Protected Routes (Requires Authentication)

Used for creating, updating, deleting:

```python
@router.post("/products", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # 🔒 This protects the route
):
    """Only authenticated users can create products"""
    return create_product(session, product_data)
```

**How it works:**
1. Client sends request with `Authorization: Bearer <token>` header
2. `Depends(get_current_active_user)` validates token
3. If valid, user object is injected into `current_user`
4. If invalid/missing, returns 401 Unauthorized automatically

## Module-Specific Differences

While the pattern is the same, each module has specific business rules:

### Catalog Module

**Unique validations:**
- Category names must be unique
- Products must have unique SKUs
- Cannot delete category with active products

```python
# Check category has no products before deleting
statement = select(Product).where(Product.category_id == category_id, not Product.is_deleted)
products = session.exec(statement).all()
if products:
    raise HTTPException(status_code=400, detail="Category has products")
```

### Inventory Module

**Unique validations:**
- Branch names should be unique
- Stock quantity cannot be negative
- Movements must reference existing products and branches

```python
# Validate stock quantity
if stock_data.quantity < 0:
    raise HTTPException(status_code=400, detail="Quantity cannot be negative")
```

### Sales Module

**Unique validations:**
- Order tracking numbers must be unique
- Order items must reference existing products
- Coupon codes must be unique
- Validate coupon usage limits

```python
# Check coupon usage
if coupon.current_uses >= coupon.max_uses:
    raise HTTPException(status_code=400, detail="Coupon usage limit reached")
```

### Logistics Module

**Unique validations:**
- Shipment tracking numbers must be unique
- One shipment per order (one-to-one relationship)
- Validate shipment status transitions

```python
# Check order doesn't already have shipment
existing_shipment = session.exec(
    select(Shipment).where(Shipment.order_id == order_id)
).first()
if existing_shipment:
    raise HTTPException(status_code=400, detail="Order already has a shipment")
```

## Testing Protected Routes

### Without Authentication (Should Fail)

```bash
curl -X POST "http://localhost:8000/api/catalog/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic products"}'

# Response: 401 Unauthorized
{
  "detail": "Not authenticated"
}
```

### With Authentication (Should Succeed)

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/token" \
  -d "username=admin@example.com&password=admin123" \
  | jq -r '.access_token')

# 2. Use token to create category
curl -X POST "http://localhost:8000/api/catalog/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic products"}'

# Response: 201 Created
{
  "id": 1,
  "name": "Electronics",
  "description": "Electronic products",
  "created_at": "2025-12-13T12:00:00Z",
  "updated_at": "2025-12-13T12:00:00Z"
}
```

## Complete Example: Product Module

Here's how all pieces fit together for the Product resource:

**Models (already exists):**
```python
class Product(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=50)
    name_product: str = Field(max_length=200)
    description: str = Field(max_length=2000)
    price: float
    category_id: int = Field(foreign_key="category.id")
```

**Schemas:**
```python
class ProductCreate(BaseModel):
    sku: str = Field(min_length=3, max_length=50)
    name_product: str = Field(min_length=2, max_length=200)
    description: str = Field(max_length=2000)
    price: float = Field(gt=0)
    category_id: int

class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name_product: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name_product: str
    description: str
    price: float
    category_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Services:**
```python
def get_products(session: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    statement = select(Product).where(not Product.is_deleted).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def create_product(session: Session, product_data: ProductCreate) -> Product:
    # Validate SKU unique
    existing = get_product_by_sku(session, product_data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    # Validate category exists
    category = get_category_by_id(session, product_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    product = Product(**product_data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

# update_product, delete_product, etc...
```

**Routes:**
```python
@router.get("/products", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    return get_products(session, skip, limit)

@router.post("/products", response_model=ProductResponse, status_code=201)
def create_new_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)  # Protected
):
    return create_product(session, product_data)
```

## Summary

### For Every Resource, Create:

1. **3 Schemas** (schema.py):
   - `{Resource}Create` - Required fields
   - `{Resource}Update` - All optional
   - `{Resource}Response` - What API returns

2. **5 Service Functions** (service.py):
   - `get_{resources}()` - List with pagination
   - `get_{resource}_by_id()` - Get one
   - `create_{resource}()` - Create with validation
   - `update_{resource}()` - Update with validation
   - `delete_{resource}()` - Soft delete

3. **5 Routes** (router.py):
   - `GET /{resources}` - Public
   - `GET /{resources}/{id}` - Public
   - `POST /{resources}` - **Protected**
   - `PATCH /{resources}/{id}` - **Protected**
   - `DELETE /{resources}/{id}` - **Protected**

### Protection Pattern:

- **Public**: No `current_user` parameter
- **Protected**: Add `current_user: User = Depends(get_current_active_user)`

This pattern repeats for **every** module: Category, Product, Branch, Order, Shipment, etc.

The only differences are:
- Field names (sku vs tracking_number vs code)
- Unique validation rules (SKU, email, coupon code)
- Business rules (can't delete category with products, etc.)

Next: See completed implementations in each module directory.
