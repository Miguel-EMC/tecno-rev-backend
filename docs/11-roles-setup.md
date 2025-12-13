# Roles Setup - User Roles and Permissions

## Overview

The system uses a role-based access control (RBAC) system with 5 predefined roles. Each role has specific permissions and responsibilities within the application.

## Available Roles

### 1. SUPER_ADMIN (ID: 1)
**Description:** System Administrator / Owner

**Capabilities:**
- Full unrestricted access to all functionalities
- Manage all branches and view consolidated financial information
- Create and delete users
- Assign roles and configure the system
- Supervise all operations across the organization

**Responsibilities:**
- Strategic oversight
- Global system configuration
- User and permission management
- Comprehensive financial analysis
- Corporate decision making

**Use Case:** Designed for the business owner or general manager

---

### 2. BRANCH_MANAGER (ID: 2)
**Description:** Branch Manager

**Capabilities:**
- Full control over assigned branch
- Manage local product inventory
- Supervise branch sales
- Manage local staff
- Generate branch reports
- Approve returns and inventory adjustments

**Restrictions:**
- NO access to other branches' financial information
- CANNOT modify global configurations

**Responsibilities:**
- Operational branch administration
- Local inventory management
- Sales and logistics team supervision
- Service quality control
- Branch sales targets achievement

**Use Case:** Store or branch managers

---

### 3. SALES_AGENT (ID: 3)
**Description:** Sales Agent / Cashier

**Capabilities:**
- Process sales at POS (Point of Sale)
- Generate invoices
- Check product availability
- Register customers
- Apply authorized discounts and coupons
- Handle payments

**Restrictions:**
- CANNOT modify prices without authorization
- NO access to financial reports
- CANNOT make inventory adjustments

**Responsibilities:**
- Customer service
- POS sales processing
- Product consulting
- Cash handling
- Sales receipt generation

**Use Case:** Counter staff and salespeople

---

### 4. LOGISTICS (ID: 4)
**Description:** Logistics / Shipping Personnel

**Capabilities:**
- Access pending shipment orders
- Mark products as packed
- Generate shipping labels
- Update delivery statuses
- Manage physical returns

**Restrictions:**
- NO access to POS sales processing
- CANNOT modify prices or inventory

**Responsibilities:**
- Order preparation and packing
- Courier company coordination
- Product verification before shipping
- Package tracking updates
- Reverse logistics (returns) management

**Use Case:** Warehouse and shipping staff

---

### 5. CUSTOMER (ID: 5)
**Description:** Customer / Web User

**Capabilities:**
- Browse product catalog
- Add items to cart
- Make online purchases
- View order history (own orders only)
- Check shipping status
- Manage personal profile

**Restrictions:**
- VERY limited access
- Can ONLY view own orders and data
- NO access to other customers' information
- NO access to administrative functions

**Responsibilities:**
- Make purchases
- Provide accurate delivery information
- Report any order issues

**Use Case:** Registered customers shopping through web/mobile platform
**Note:** This is the default role for new registrations

---

## Initial Setup

### Step 1: Create Roles in Database

Run the seed script to populate the roles table:

```bash
python scripts/seed_roles_final.py
```

**Expected Output:**
```
Iniciando creación de roles...

✓ Rol 'SUPER_ADMIN' creado exitosamente (ID: 1)
✓ Rol 'BRANCH_MANAGER' creado exitosamente (ID: 2)
✓ Rol 'SALES_AGENT' creado exitosamente (ID: 3)
✓ Rol 'LOGISTICS' creado exitosamente (ID: 4)
✓ Rol 'CUSTOMER' creado exitosamente (ID: 5)

============================================================
¡Todos los roles han sido creados exitosamente!
============================================================
```

### Step 2: Verify Roles

Check that all roles were created correctly:

```python
from sqlmodel import Session, select
from app.core.database import engine
from app.modules.auth.models import Role

with Session(engine) as session:
    roles = session.exec(select(Role)).all()
    for role in roles:
        print(f"{role.id}: {role.name.value}")
```

**Output:**
```
1: SUPER_ADMIN
2: BRANCH_MANAGER
3: SALES_AGENT
4: LOGISTICS
5: CUSTOMER
```

---

## Role Assignment

### During Registration

Users are assigned a role during registration. The default role is `CUSTOMER` (ID: 5).

**Example - Register as Customer:**
```json
POST /api/auth/register
{
  "email": "customer@example.com",
  "password": "securepass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": 1234567890,
  "role_id": 5  // CUSTOMER (default)
}
```

**Example - Admin Creating a Branch Manager:**
```json
POST /api/auth/register
{
  "email": "manager@branch1.com",
  "password": "securepass123",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": 9876543210,
  "role_id": 2,      // BRANCH_MANAGER
  "branch_id": 1     // Assigned to Branch 1
}
```

### Updating User Role

Only users with appropriate permissions can change roles:

```json
PATCH /api/auth/profile
{
  "role_id": 3  // Change to SALES_AGENT
}
```

---

## Role Enum Definition

Roles are defined as an enum in the codebase:

**File:** `app/modules/auth/enums.py`

```python
from enum import Enum

class UserRole(str, Enum):
    """User roles in the system"""

    SUPER_ADMIN = "SUPER_ADMIN"      # Owner: Sees all branches and finances
    BRANCH_MANAGER = "BRANCH_MANAGER" # Manager: Controls THEIR branch and THEIR stock
    SALES_AGENT = "SALES_AGENT"      # Salesperson: Sells at POS and attends counter
    LOGISTICS = "LOGISTICS"          # Shipping handler: Prepares packages
    CUSTOMER = "CUSTOMER"            # Web buyer: Only sees their orders
```

---

## Database Schema

**Table:** `role`

| Column        | Type      | Description                           |
|---------------|-----------|---------------------------------------|
| id            | INTEGER   | Primary key                           |
| name          | ENUM      | Role name (UserRole enum)             |
| description   | VARCHAR   | Detailed role description             |
| created_at    | TIMESTAMP | Creation timestamp                    |
| updated_at    | TIMESTAMP | Last update timestamp                 |
| is_deleted    | BOOLEAN   | Soft delete flag                      |

**Relationship:**
- One role can have many users
- Each user has exactly one role

---

## Important Notes

### Security Considerations

1. **Role Hierarchy:** SUPER_ADMIN has the highest privileges
2. **Immutable IDs:** Role IDs should remain constant (1-5)
3. **Default Role:** New registrations default to CUSTOMER (ID: 5)
4. **Branch Assignment:** BRANCH_MANAGER and SALES_AGENT require a `branch_id`

### Best Practices

1. **Never delete roles** - Use soft delete (`is_deleted` flag)
2. **Audit role changes** - Track who modified user roles
3. **Validate permissions** - Check role before allowing sensitive operations
4. **Document custom roles** - If adding new roles, document thoroughly

### Common Scenarios

**Scenario 1: Creating First Admin**
```python
# After seeding roles, create your first admin user
POST /api/auth/register
{
  "email": "admin@company.com",
  "password": "very_secure_password",
  "first_name": "Admin",
  "last_name": "User",
  "phone": 5551234567,
  "role_id": 1  // SUPER_ADMIN
}
```

**Scenario 2: New Employee at Branch**
```python
# Branch manager or admin creates a sales agent
POST /api/auth/register
{
  "email": "seller@branch1.com",
  "password": "secure_password",
  "first_name": "Sales",
  "last_name": "Person",
  "phone": 5559876543,
  "role_id": 3,      // SALES_AGENT
  "branch_id": 1     // Branch 1
}
```

**Scenario 3: Customer Self-Registration**
```python
# Default registration from website
POST /api/auth/register
{
  "email": "customer@email.com",
  "password": "mypassword",
  "first_name": "Customer",
  "last_name": "Name",
  "phone": 5551112222
  // role_id defaults to 5 (CUSTOMER)
  // branch_id is null for customers
}
```

---

## Troubleshooting

### Issue: "Role not found"

**Cause:** Roles table is empty

**Solution:** Run the seed script:
```bash
python scripts/seed_roles_final.py
```

### Issue: "Invalid role_id"

**Cause:** Trying to assign a non-existent role

**Solution:** Use only role IDs 1-5

### Issue: "Foreign key constraint failed"

**Cause:** Role enum in code doesn't match database enum

**Solution:** Ensure enum values are uppercase:
```python
SUPER_ADMIN = "SUPER_ADMIN"  # ✅ Correct
super_admin = "super_admin"  # ❌ Wrong
```

---

## Next Steps

- Implement role-based route protection
- Add permission decorators
- Create admin dashboard for role management
- Implement role-based UI rendering
- Add audit logging for role changes

---

## Related Documentation

- [Authentication Schemas](06-auth-schemas.md)
- [Authentication Services](07-auth-services.md)
- [Authentication Routes](08-auth-routes.md)
- [Models & Relationships](04-models-relationships.md)
