# Models and Relationships with SQLModel

This guide covers creating database models using SQLModel and implementing different types of relationships.

## What is SQLModel?

SQLModel combines:
- **SQLAlchemy**: Powerful ORM for database operations
- **Pydantic**: Data validation and serialization

This gives you:
- Type safety
- Automatic API documentation
- Data validation
- Database operations

## Basic Model Structure

### Creating a Simple Model

```python
from typing import Optional
from sqlmodel import SQLModel, Field

class Category(SQLModel, table=True):
    """Product category model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
```

### Key Components

1. **Inherit from `SQLModel`**: Base class for all models
2. **`table=True`**: Creates actual database table
3. **Type annotations**: Define column types (`str`, `int`, `float`, etc.)
4. **`Field()`**: Configure column properties

### Field Parameters

```python
from sqlmodel import Field

class Product(SQLModel, table=True):
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Unique constraint + index
    sku: str = Field(unique=True, index=True, max_length=50)

    # Required field with max length
    name_product: str = Field(max_length=200)

    # Optional field
    description: Optional[str] = Field(default=None, max_length=2000)

    # Default value
    price: float = Field(default=0.0)

    # Foreign key
    category_id: int = Field(foreign_key="category.id")
```

## Using Mixins for Reusable Fields

### The AuditMixin Pattern

Instead of repeating audit fields in every model, create a mixin:

```python
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

def utc_now() -> datetime:
    """Returns current UTC time as timezone-aware datetime"""
    return datetime.now(timezone.utc)

class AuditMixin(SQLModel):
    """Mixin for common audit fields"""
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
```

### Using the Mixin

```python
class Product(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=50)
    name_product: str = Field(max_length=200)
    # ... automatically inherits all audit fields
```

Every model now has:
- `created_at`, `updated_at`: Timestamps
- `created_by_id`, `updated_by_id`: Who made changes
- `is_deleted`, `deleted_at`, `deleted_by_id`: Soft delete support

## Enumerations

Use enums for fields with predefined values:

```python
from enum import Enum

class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
```

Use in models:

```python
from .enums import OrderStatus

class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
```

Benefits:
- Type safety
- Auto-validation
- Clear allowed values
- IDE autocomplete

## Database Relationships

SQLModel supports three types of relationships:

1. **One-to-Many**: One record relates to multiple records
2. **One-to-One**: One record relates to exactly one other record
3. **Many-to-Many**: Multiple records relate to multiple records

### One-to-Many Relationship

**Example**: One Category has many Products

```python
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.core.mixins import AuditMixin

if TYPE_CHECKING:
    # Forward references for type hints
    from app.modules.inventory.models import StockEntry

class Category(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=200)

    # Relationship: One category → Many products
    products: List["Product"] = Relationship(back_populates="category")


class Product(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=50)
    name_product: str = Field(max_length=200)
    price: float

    # Foreign key
    category_id: int = Field(foreign_key="category.id")

    # Relationship: Many products → One category
    category: Optional["Category"] = Relationship(back_populates="products")
    stock_entries: List["StockEntry"] = Relationship(back_populates="product")
```

#### Usage

```python
# Get all products in a category
category = session.get(Category, 1)
products = category.products  # List of Product objects

# Get product's category
product = session.get(Product, 1)
category_name = product.category.name
```

### One-to-One Relationship

**Example**: One Order has one Shipment

```python
class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    total_amount: float

    # Relationship: One order → One shipment
    shipment: Optional["Shipment"] = Relationship(back_populates="order")


class Shipment(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    carrier: str

    # Foreign key with unique constraint = one-to-one
    order_id: int = Field(foreign_key="order.id", unique=True)

    # Relationship: One shipment → One order
    order: "Order" = Relationship(back_populates="shipment")
```

**Key point**: `unique=True` on the foreign key makes it one-to-one.

#### Usage

```python
# Get order's shipment
order = session.get(Order, 1)
if order.shipment:
    carrier = order.shipment.carrier

# Get shipment's order
shipment = session.get(Shipment, 1)
order_total = shipment.order.total_amount
```

### Many-to-Many Relationship

**Example**: Products in different Branches (through StockEntry)

For many-to-many relationships, use a **pivot table** (also called junction table):

```python
class Branch(AuditMixin, table=True):
    """Store branch"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name_branch: str
    address: str

    # Relationship through pivot table
    stock_entries: List["StockEntry"] = Relationship(back_populates="branch")


class Product(AuditMixin, table=True):
    """Product"""
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(unique=True, index=True, max_length=50)
    name_product: str = Field(max_length=200)

    # Relationship through pivot table
    stock_entries: List["StockEntry"] = Relationship(back_populates="product")


class StockEntry(AuditMixin, table=True):
    """Pivot table: Stock quantity per product per branch"""

    # Composite primary key
    branch_id: int = Field(foreign_key="branch.id", primary_key=True)
    product_id: int = Field(foreign_key="product.id", primary_key=True)

    # Additional data on the relationship
    quantity: int = Field(default=0)

    # Relationships
    branch: "Branch" = Relationship(back_populates="stock_entries")
    product: "Product" = Relationship(back_populates="stock_entries")
```

#### Why Use a Pivot Table?

Benefits:
1. **Store additional data**: `quantity` in this example
2. **Composite primary key**: Unique combination of `branch_id` + `product_id`
3. **Query flexibility**: Easy to find products in a branch or branches with a product

#### Usage

```python
# Get all products in a branch
branch = session.get(Branch, 1)
for stock_entry in branch.stock_entries:
    product = stock_entry.product
    quantity = stock_entry.quantity
    print(f"{product.name_product}: {quantity} units")

# Get all branches that have a product
product = session.get(Product, 1)
for stock_entry in product.stock_entries:
    branch = stock_entry.branch
    quantity = stock_entry.quantity
    print(f"Branch {branch.name_branch}: {quantity} units")
```

## Advanced Relationships

### Self-Referencing Relationships

**Example**: User referencing User (for audit fields)

```python
class User(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    first_name: str = Field(index=True, max_length=200)
    last_name: str = Field(index=True, max_length=200)

    role_id: int = Field(foreign_key="role.id")
    branch_id: Optional[int] = Field(default=None, foreign_key="branch.id")

    # Relationships
    role: Optional["Role"] = Relationship(back_populates="users")
    branch: Optional["Branch"] = Relationship(back_populates="users")
    orders: List["Order"] = Relationship(back_populates="customer")
```

The `AuditMixin` already has self-referencing foreign keys:
- `created_by_id` → `user.id`
- `updated_by_id` → `user.id`
- `deleted_by_id` → `user.id`

### Multiple Relationships to Same Table

**Example**: Order has both customer and fulfillment branch

```python
class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Multiple foreign keys to same table
    customer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    fulfillment_branch_id: int = Field(foreign_key="branch.id")

    # Different relationship names
    customer: Optional["User"] = Relationship(back_populates="orders")
    fulfillment_branch: "Branch" = Relationship(back_populates="orders")
```

## Complex Example: Complete Order System

```python
# Order with items
class Order(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_number: str = Field(unique=True, index=True)
    total_amount: float
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)

    customer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    fulfillment_branch_id: int = Field(foreign_key="branch.id")

    # Relationships
    customer: Optional["User"] = Relationship(back_populates="orders")
    fulfillment_branch: "Branch" = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    shipment: Optional["Shipment"] = Relationship(back_populates="order")


class OrderItem(AuditMixin, table=True):
    """Items in an order"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: float

    # Relationships
    order: "Order" = Relationship(back_populates="items")
    product: "Product" = Relationship()
```

### Usage

```python
# Get order with all details
order = session.get(Order, 1)

# Access customer
customer_name = f"{order.customer.first_name} {order.customer.last_name}"

# Access items
for item in order.items:
    product_name = item.product.name_product
    total_price = item.quantity * item.unit_price
    print(f"{product_name}: {item.quantity} x ${item.unit_price} = ${total_price}")

# Access shipment
if order.shipment:
    print(f"Shipped via {order.shipment.carrier}")
```

## TYPE_CHECKING for Circular Imports

Use `TYPE_CHECKING` to avoid circular import issues:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These imports only happen during type checking, not at runtime
    from app.modules.sales.models import Order
    from app.modules.catalog.models import Product

class Branch(AuditMixin, table=True):
    orders: List["Order"] = Relationship(back_populates="fulfillment_branch")
```

## Best Practices

### 1. Always Use Indexes

Add indexes on:
- Foreign keys (usually automatic)
- Fields used in WHERE clauses
- Fields used in ORDER BY
- Unique fields

```python
email: str = Field(index=True, unique=True)
status: OrderStatus = Field(index=True)
```

### 2. Set Max Length on Strings

Prevents performance issues:

```python
name: str = Field(max_length=200)
description: str = Field(max_length=2000)
```

### 3. Use Optional Correctly

```python
# Required field
name: str

# Optional field
description: Optional[str] = None

# Required but can be set later
id: Optional[int] = Field(default=None, primary_key=True)
```

### 4. Name Foreign Keys Clearly

```python
# Good
customer_id: int = Field(foreign_key="user.id")
fulfillment_branch_id: int = Field(foreign_key="branch.id")

# Bad
user: int = Field(foreign_key="user.id")  # Confusing with relationship
branch: int = Field(foreign_key="branch.id")
```

### 5. Use Soft Delete

Instead of deleting records, mark them as deleted:

```python
# Don't do this
session.delete(product)

# Do this
product.is_deleted = True
product.deleted_at = utc_now()
product.deleted_by_id = current_user.id
session.add(product)
session.commit()
```

## Next Steps

- [Database Migrations](./05-migrations.md) - Learn how to create and apply migrations with Alembic
