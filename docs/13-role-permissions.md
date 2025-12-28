# Role-Based Permissions - Route Protection

## Overview

This guide explains how to implement role-based access control (RBAC) to protect API routes based on user roles.

**Important:** Security is enforced on the **BACKEND**, not the frontend. The frontend only hides UI elements for better user experience, but the server validates all permissions.

## Permission System

### File: `app/core/permissions.py`

The permission system uses FastAPI dependencies to check user roles before allowing access to routes.

```python
from app.core.permissions import require_admin, require_manager, require_staff

@router.get("/admin-only")
def admin_route(current_user: User = Depends(require_admin)):
    """Only SUPER_ADMIN can access this"""
    return {"message": "Admin access granted"}
```

### Available Permission Checkers

| Permission Checker      | Allowed Roles                                        | Use Case                          |
|-------------------------|------------------------------------------------------|-----------------------------------|
| `require_admin`         | SUPER_ADMIN                                          | Admin-only operations             |
| `require_manager`       | SUPER_ADMIN, BRANCH_MANAGER                          | Management operations             |
| `require_staff`         | SUPER_ADMIN, BRANCH_MANAGER, SALES_AGENT             | Staff operations                  |
| `require_logistics`     | SUPER_ADMIN, LOGISTICS                               | Shipping operations               |
| `require_authenticated` | All roles (any logged-in user)                       | General authenticated routes      |
| `require_role(role)`    | Specific role only                                   | Single role restriction           |
| `require_any_role(...)`| Any of the specified roles                           | Custom role combinations          |

### Custom Permission Checkers

```python
from app.modules.auth.enums import UserRole
from app.core.permissions import require_role, require_any_role

# Only SALES_AGENT
only_sales = require_role(UserRole.SALES_AGENT)

# SALES_AGENT or CUSTOMER
sales_or_customer = require_any_role(UserRole.SALES_AGENT, UserRole.CUSTOMER)

@router.get("/sales-only")
def sales_route(current_user: User = Depends(only_sales)):
    return {"message": "Sales access"}
```

## Route Examples by Module

### 1. User Management (Admin)

**File:** `app/modules/auth/admin_routes.py`

```python
from app.core.permissions import require_admin

@router.get("/api/admin/users")
def list_all_users(current_user: User = Depends(require_admin)):
    """
    List all users - SUPER_ADMIN only
    """
    pass

@router.post("/api/admin/users")
def create_user(current_user: User = Depends(require_admin)):
    """
    Create new user - SUPER_ADMIN only
    """
    pass

@router.delete("/api/admin/users/{user_id}")
def delete_user(current_user: User = Depends(require_admin)):
    """
    Delete user - SUPER_ADMIN only
    """
    pass
```

### 2. Inventory Management

**Permissions:**
- **SUPER_ADMIN**: Full access to all branches
- **BRANCH_MANAGER**: Access to their branch only
- **SALES_AGENT**: Read-only access to their branch

```python
from app.core.permissions import require_manager, require_staff

@router.post("/api/inventory/stock")
def add_stock(
    stock_data: StockCreate,
    current_user: User = Depends(require_manager),  # Admin or Manager
    session: Session = Depends(get_session)
):
    """
    Add stock to inventory.
    Required: SUPER_ADMIN or BRANCH_MANAGER
    """

    # Branch managers can only add to their branch
    if current_user.role.name == UserRole.BRANCH_MANAGER:
        if stock_data.branch_id != current_user.branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only manage your own branch"
            )

    # Create stock entry
    pass


@router.get("/api/inventory/stock")
def get_stock(
    current_user: User = Depends(require_staff),  # Admin, Manager, or Sales
    session: Session = Depends(get_session)
):
    """
    Get stock information.
    Required: SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT
    """

    # Filter by branch for non-admin users
    if current_user.role.name == UserRole.SUPER_ADMIN:
        # Can see all branches
        statement = select(StockEntry)
    else:
        # Can only see their branch
        statement = select(StockEntry).where(
            StockEntry.branch_id == current_user.branch_id
        )

    stocks = session.exec(statement).all()
    return stocks
```

### 3. Sales / Orders

**Permissions:**
- **SUPER_ADMIN**: View all orders
- **BRANCH_MANAGER**: View/manage orders from their branch
- **SALES_AGENT**: Create orders, view their branch's orders
- **CUSTOMER**: View only their own orders

```python
from app.core.permissions import require_staff, require_authenticated

@router.post("/api/orders")
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(require_staff),  # Staff or higher
    session: Session = Depends(get_session)
):
    """
    Create a new order.
    Required: SUPER_ADMIN, BRANCH_MANAGER, or SALES_AGENT
    """
    # Sales agents can only create orders for their branch
    if current_user.role.name == UserRole.SALES_AGENT:
        order_data.fulfillment_branch_id = current_user.branch_id

    # Create order
    pass


@router.get("/api/orders")
def get_orders(
    current_user: User = Depends(require_authenticated),  # Any user
    session: Session = Depends(get_session)
):
    """
    Get orders based on user role.
    Required: Any authenticated user
    """

    if current_user.role.name == UserRole.SUPER_ADMIN:
        # See all orders
        statement = select(Order)

    elif current_user.role.name in [UserRole.BRANCH_MANAGER, UserRole.SALES_AGENT]:
        # See only their branch's orders
        statement = select(Order).where(
            Order.fulfillment_branch_id == current_user.branch_id
        )

    elif current_user.role.name == UserRole.CUSTOMER:
        # See only their own orders
        statement = select(Order).where(
            Order.customer_id == current_user.id
        )

    else:
        # LOGISTICS should not access orders directly
        raise HTTPException(status_code=403, detail="Access denied")

    orders = session.exec(statement).all()
    return orders


@router.get("/api/orders/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(require_authenticated),
    session: Session = Depends(get_session)
):
    """
    Get specific order with permission checks.
    """
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check permissions
    if current_user.role.name == UserRole.CUSTOMER:
        # Customers can only see their own orders
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role.name in [UserRole.BRANCH_MANAGER, UserRole.SALES_AGENT]:
        # Staff can only see orders from their branch
        if order.fulfillment_branch_id != current_user.branch_id:
            raise HTTPException(status_code=403, detail="Access denied")

    # SUPER_ADMIN can see everything (no check needed)

    return order
```

### 4. Logistics / Shipments

**Permissions:**
- **SUPER_ADMIN**: Full access
- **LOGISTICS**: Manage shipments
- **CUSTOMER**: View their shipment status

```python
from app.core.permissions import require_logistics, require_authenticated

@router.post("/api/shipments")
def create_shipment(
    shipment_data: ShipmentCreate,
    current_user: User = Depends(require_logistics),  # Admin or Logistics
    session: Session = Depends(get_session)
):
    """
    Create a shipment.
    Required: SUPER_ADMIN or LOGISTICS
    """
    pass


@router.patch("/api/shipments/{shipment_id}/status")
def update_shipment_status(
    shipment_id: int,
    status_data: ShipmentStatusUpdate,
    current_user: User = Depends(require_logistics),  # Admin or Logistics
    session: Session = Depends(get_session)
):
    """
    Update shipment status.
    Required: SUPER_ADMIN or LOGISTICS
    """
    pass


@router.get("/api/shipments/{shipment_id}")
def get_shipment(
    shipment_id: int,
    current_user: User = Depends(require_authenticated),
    session: Session = Depends(get_session)
):
    """
    Get shipment details.
    Any authenticated user can view, but filtered by permission.
    """
    shipment = session.get(Shipment, shipment_id)

    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    # Customers can only see their own shipments
    if current_user.role.name == UserRole.CUSTOMER:
        if shipment.order.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return shipment
```

### 5. Product Catalog

**Permissions:**
- **Public**: Read products (no auth required)
- **SUPER_ADMIN**: Create/update/delete products
- **BRANCH_MANAGER**: Update product details

```python
from app.core.permissions import require_manager

# Public route - NO authentication required
@router.get("/api/products")
def list_products(session: Session = Depends(get_session)):
    """
    List all products - PUBLIC endpoint
    No authentication required
    """
    statement = select(Product).where(Product.is_deleted == False)
    products = session.exec(statement).all()
    return products


@router.post("/api/products")
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_admin),  # SUPER_ADMIN only
    session: Session = Depends(get_session)
):
    """
    Create a product.
    Required: SUPER_ADMIN
    """
    pass


@router.patch("/api/products/{product_id}")
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_manager),  # Admin or Manager
    session: Session = Depends(get_session)
):
    """
    Update product details.
    Required: SUPER_ADMIN or BRANCH_MANAGER
    """
    pass


@router.delete("/api/products/{product_id}")
def delete_product(
    product_id: int,
    current_user: User = Depends(require_admin),  # SUPER_ADMIN only
    session: Session = Depends(get_session)
):
    """
    Delete a product.
    Required: SUPER_ADMIN
    """
    pass
```

## Permission Matrix

| Route                    | Public | Customer | Sales | Logistics | Manager | Admin |
|--------------------------|--------|----------|-------|-----------|---------|-------|
| **Products**             |        |          |       |           |         |       |
| GET /products            | ✅     | ✅       | ✅    | ✅        | ✅      | ✅    |
| POST /products           | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |
| PATCH /products/{id}     | ❌     | ❌       | ❌    | ❌        | ✅      | ✅    |
| DELETE /products/{id}    | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |
| **Orders**               |        |          |       |           |         |       |
| GET /orders (own)        | ❌     | ✅       | ❌    | ❌        | ❌      | ✅    |
| GET /orders (branch)     | ❌     | ❌       | ✅    | ❌        | ✅      | ✅    |
| GET /orders (all)        | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |
| POST /orders             | ❌     | ✅       | ✅    | ❌        | ✅      | ✅    |
| **Inventory**            |        |          |       |           |         |       |
| GET /stock               | ❌     | ❌       | ✅    | ❌        | ✅      | ✅    |
| POST /stock              | ❌     | ❌       | ❌    | ❌        | ✅      | ✅    |
| **Shipments**            |        |          |       |           |         |       |
| GET /shipments (own)     | ❌     | ✅       | ❌    | ❌        | ❌      | ✅    |
| POST /shipments          | ❌     | ❌       | ❌    | ✅        | ❌      | ✅    |
| PATCH /shipments/status  | ❌     | ❌       | ❌    | ✅        | ❌      | ✅    |
| **Users**                |        |          |       |           |         |       |
| GET /admin/users         | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |
| POST /admin/users        | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |
| DELETE /admin/users/{id} | ❌     | ❌       | ❌    | ❌        | ❌      | ✅    |

## Testing Permissions

### 1. Create Users with Different Roles

```bash
# Create SUPER_ADMIN
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"pass123","first_name":"Admin","last_name":"User","phone":1234567890,"role_id":1}'

# Create CUSTOMER
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@test.com","password":"pass123","first_name":"Customer","last_name":"User","phone":1234567890,"role_id":5}'
```

### 2. Login and Get Tokens

```bash
# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"pass123"}' \
  | jq -r '.access_token')

# Login as customer
CUSTOMER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@test.com","password":"pass123"}' \
  | jq -r '.access_token')
```

### 3. Test Permissions

```bash
# Admin can access admin routes
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# ✅ Success

# Customer cannot access admin routes
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer $CUSTOMER_TOKEN"
# ❌ 403 Forbidden
```

## Frontend Integration

### What the Frontend Should Do

```javascript
// Store user role from login response
const loginUser = async (email, password) => {
  const response = await fetch('/api/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);

  // Get user profile to know the role
  const profileResponse = await fetch('/api/auth/profile', {
    headers: { 'Authorization': `Bearer ${data.access_token}` }
  });

  const profile = await profileResponse.json();
  localStorage.setItem('user_role', profile.role_id);

  return profile;
};

// Hide/show UI elements based on role
const UserManagementButton = () => {
  const userRole = localStorage.getItem('user_role');

  // Only show to SUPER_ADMIN (role_id = 1)
  if (userRole !== '1') {
    return null;  // Hide button
  }

  return <button>Manage Users</button>;
};
```

**Important:** The frontend ONLY hides UI for better UX. The backend ALWAYS validates permissions.

## Common Patterns

### Pattern 1: Branch-Scoped Access

```python
def check_branch_access(
    resource_branch_id: int,
    current_user: User
):
    """Ensure user can only access their own branch resources"""
    if current_user.role.name == UserRole.SUPER_ADMIN:
        return  # Admin can access all branches

    if current_user.branch_id != resource_branch_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access resources from your branch"
        )
```

### Pattern 2: Owner-Only Access

```python
def check_ownership(
    resource_owner_id: int,
    current_user: User
):
    """Ensure user can only access their own resources"""
    if current_user.role.name == UserRole.SUPER_ADMIN:
        return  # Admin can access everything

    if current_user.id != resource_owner_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own resources"
        )
```

### Pattern 3: Conditional Filtering

```python
def get_filtered_query(model, current_user: User):
    """Return query filtered based on user role"""
    statement = select(model)

    if current_user.role.name == UserRole.SUPER_ADMIN:
        # No filter - see everything
        pass
    elif current_user.role.name in [UserRole.BRANCH_MANAGER, UserRole.SALES_AGENT]:
        # Filter by branch
        statement = statement.where(model.branch_id == current_user.branch_id)
    elif current_user.role.name == UserRole.CUSTOMER:
        # Filter by ownership
        statement = statement.where(model.customer_id == current_user.id)

    return statement
```

## Best Practices

1. **Always validate on backend** - Never trust frontend-only validation
2. **Use dependencies** - Leverage FastAPI's dependency injection
3. **Be explicit** - Clearly document which roles can access each route
4. **Test permissions** - Write tests for each permission scenario
5. **Log access** - Track who accesses sensitive routes
6. **Fail secure** - Default to deny access if unsure

## Next Steps

- Implement audit logging for sensitive operations
- Add field-level permissions (e.g., only admins can change role_id)
- Create permission groups for complex scenarios
- Add IP whitelisting for admin routes
- Implement rate limiting per role

## Related Documentation

- [Roles Setup](./11-roles-setup.md)
- [JWT Tokens](./12-jwt-tokens.md)
- [Authentication Services](./07-auth-services.md)
