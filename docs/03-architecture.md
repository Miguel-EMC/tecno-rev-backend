# Project Architecture

This guide explains the folder structure and architectural patterns used in this FastAPI project.

## Project Structure

```
tecno-rev-backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── app/                       # Main application code
│   ├── core/                  # Core utilities and config
│   │   ├── database.py       # Database connection
│   │   └── mixins.py         # Reusable model mixins
│   ├── modules/              # Feature modules
│   │   ├── auth/            # Authentication & users
│   │   ├── catalog/         # Products & categories
│   │   ├── inventory/       # Stock management
│   │   ├── logistics/       # Shipments
│   │   └── sales/           # Orders & coupons
│   ├── main.py              # FastAPI app entry point
│   └── models.py            # Central model imports
├── docs/                     # Documentation
├── .env                      # Environment variables
├── .gitignore
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Docker setup
├── pyproject.toml           # Project dependencies
└── uv.lock                  # Locked dependencies
```

## Architecture Pattern: Modular Monolith

This project follows a **modular monolith** architecture, where related features are grouped into self-contained modules.

### Benefits

1. **Clear separation of concerns**: Each module handles one domain
2. **Easy to navigate**: Find all code for a feature in one place
3. **Scalable**: Can split modules into microservices later if needed
4. **Team-friendly**: Different developers can work on different modules

## Module Structure

Each module follows the same consistent structure:

```
app/modules/<module_name>/
├── enums.py      # Enumerations (status, types, etc.)
├── models.py     # SQLModel database models
├── schema.py     # Pydantic schemas (request/response)
├── router.py     # FastAPI route endpoints
└── service.py    # Business logic
```

### Example: Sales Module

```
app/modules/sales/
├── enums.py      # OrderType, OrderStatus
├── models.py     # Order, OrderItem, Coupon
├── schema.py     # OrderCreate, OrderResponse
├── router.py     # POST /orders, GET /orders
└── service.py    # create_order(), calculate_total()
```

## Layer Responsibilities

### 1. Models (`models.py`)

**Purpose**: Define database tables using SQLModel

```python
from sqlmodel import Field
from app.core.mixins import AuditMixin

class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    total_amount: float
    status: OrderStatus = Field(default=OrderStatus.PENDING)
```

**Responsibilities:**
- Database table structure
- Relationships between tables
- Database constraints (unique, index, foreign keys)

### 2. Schemas (`schema.py`)

**Purpose**: Define API request/response formats using Pydantic

```python
from pydantic import BaseModel, EmailStr

class OrderCreate(BaseModel):
    """Request schema for creating an order"""
    customer_id: int
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    """Response schema for order data"""
    id: int
    tracking_number: str
    total_amount: float
    status: str
```

**Responsibilities:**
- API input validation
- Response formatting
- Data transformation
- Documentation (auto-generated from schemas)

### 3. Routers (`router.py`)

**Purpose**: Define HTTP endpoints

```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    session: Session = Depends(get_session)
):
    """Create a new order"""
    return service.create_order(session, order)
```

**Responsibilities:**
- Define HTTP routes (GET, POST, PUT, DELETE)
- Handle request/response
- Dependency injection
- Route documentation

### 4. Services (`service.py`)

**Purpose**: Business logic layer

```python
from sqlmodel import Session, select

def create_order(session: Session, order_data: OrderCreate) -> Order:
    """Create order with business logic"""
    # Calculate total
    total = calculate_total(order_data.items)

    # Create order
    order = Order(
        customer_id=order_data.customer_id,
        total_amount=total,
        status=OrderStatus.PENDING
    )

    session.add(order)
    session.commit()
    session.refresh(order)

    return order
```

**Responsibilities:**
- Business logic
- Data validation (business rules)
- Database queries
- Transaction management

### 5. Enums (`enums.py`)

**Purpose**: Define enumeration types

```python
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
```

**Responsibilities:**
- Type-safe constants
- Allowed values for fields
- Auto-documentation

## Core Components

### `app/core/mixins.py`

Reusable model components:

```python
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class AuditMixin(SQLModel):
    """Add audit fields to any model"""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
```

**Benefits:**
- **DRY** (Don't Repeat Yourself): Write once, use everywhere
- **Soft Delete**: Mark records as deleted instead of removing them
- **Audit Trail**: Track who created/updated/deleted records

### `app/core/database.py`

Centralized database connection:

```python
from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Session:
    with Session(engine) as session:
        yield session
```

### `app/models.py`

Central import file for Alembic:

```python
"""
Central import for all SQLModel models.
This ensures Alembic can detect all models for migrations.
"""
from app.modules.auth.models import User, Role
from app.modules.catalog.models import Category, Product, ProductImage
from app.modules.inventory.models import Branch, StockEntry, InventoryMovement
from app.modules.sales.models import Order, OrderItem, Coupon
from app.modules.logistics.models import Shipment

__all__ = [
    "User", "Role", "Category", "Product", "ProductImage",
    "Branch", "StockEntry", "InventoryMovement",
    "Order", "OrderItem", "Coupon", "Shipment"
]
```

**Important:** All models must be imported here for Alembic auto-detection.

## Request Flow

Here's how a request flows through the application:

```
1. Client Request
   ↓
2. Router (router.py) - Receives HTTP request
   ↓
3. Schema (schema.py) - Validates input data
   ↓
4. Service (service.py) - Executes business logic
   ↓
5. Model (models.py) - Interacts with database
   ↓
6. Database - Stores/retrieves data
   ↓
7. Model → Service → Schema → Router
   ↓
8. Client Response (JSON)
```

### Example Flow: Create Order

```python
# 1. Client sends POST request
POST /orders
{
  "customer_id": 1,
  "items": [...]
}

# 2. Router receives request
@router.post("/orders")
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    # 3. Schema validates data (OrderCreate)
    # 4. Call service layer
    return service.create_order(session, order)

# 5. Service executes business logic
def create_order(session: Session, order_data: OrderCreate):
    # 6. Model interacts with database
    order = Order(...)
    session.add(order)
    session.commit()
    return order

# 7. Response flows back through layers
# 8. Client receives JSON response
```

## Design Principles

### 1. Separation of Concerns

Each layer has a specific responsibility:
- **Routers**: Handle HTTP
- **Schemas**: Validate data
- **Services**: Business logic
- **Models**: Database operations

### 2. Dependency Injection

FastAPI's `Depends()` provides clean dependency management:

```python
def create_order(
    session: Session = Depends(get_session),  # Auto-injected
    current_user: User = Depends(get_current_user)  # Auto-injected
):
    pass
```

### 3. Type Safety

SQLModel + Pydantic provide full type safety:

```python
def get_user(user_id: int) -> User:  # Type hints everywhere
    user: User = session.get(User, user_id)
    return user
```

### 4. Reusability

Mixins and utilities prevent code duplication:

```python
class Order(AuditMixin, table=True):  # Inherits audit fields
    pass

class Product(AuditMixin, table=True):  # Same audit fields
    pass
```

## Module Dependencies

```
app/core/
  ↓ (used by)
app/modules/*
  ↓ (registered in)
app/main.py
```

Modules should:
- ✅ Depend on `app/core/`
- ✅ Use other modules' models (through relationships)
- ❌ NOT import from other modules' services/routers

## Next Steps

- [Models & Relationships](./04-models-relationships.md) - Learn how to create database models
- [Database Migrations](./05-migrations.md) - Manage schema changes with Alembic
