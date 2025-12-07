# Database Migrations with Alembic

This guide covers using Alembic to manage database schema changes with SQLModel.

## Why Use Alembic?

Instead of recreating tables on every restart (`SQLModel.metadata.create_all()`), Alembic provides:

1. **Version Control**: Track schema changes over time
2. **Team Collaboration**: Share database changes via migration files
3. **Rollback Capability**: Revert changes if needed
4. **Production Safety**: Apply incremental changes without data loss
5. **Migration History**: See exactly what changed and when

## Installing Alembic

```bash
uv add alembic
```

## Initializing Alembic

### 1. Initialize Alembic in Your Project

```bash
alembic init alembic
```

This creates:
```
├── alembic/
│   ├── env.py              # Alembic configuration
│   ├── script.py.mako      # Migration template
│   └── versions/           # Migration files go here
└── alembic.ini             # Alembic settings
```

### 2. Configure `alembic.ini`

Update the database URL setting:

```ini
# alembic.ini

[alembic]
script_location = %(here)s/alembic
prepend_sys_path = .

# Don't set this directly, we'll use .env instead
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### 3. Configure `alembic/env.py`

This is the most important configuration file. Here's the complete setup:

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
from sqlmodel import SQLModel
from sqlmodel.sql.sqltypes import AutoString
from dotenv import load_dotenv

load_dotenv()

# Import all models for Alembic auto-detection
from app.models import *  # noqa: E402, F403, F401

# Alembic Config object
config = context.config

# Load database URL from environment
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set metadata for autogenerate
target_metadata = SQLModel.metadata


def render_item(type_, obj, autogen_context):
    """Render SQLModel types as standard SQLAlchemy types in migrations."""
    if isinstance(type_, AutoString):
        # Preserve length if specified
        if type_.length:
            return f"sa.String(length={type_.length})"
        return "sa.String()"
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Key Configuration Points

#### 1. Import All Models

```python
from app.models import *
```

This imports from `app/models.py` which contains all model imports:

```python
# app/models.py
from app.modules.auth.models import User, Role
from app.modules.catalog.models import Category, Product, ProductImage
from app.modules.inventory.models import Branch, StockEntry, InventoryMovement
from app.modules.sales.models import Order, OrderItem, Coupon
from app.modules.logistics.models import Shipment

__all__ = [...]
```

**Important:** Every new model MUST be imported in `app/models.py` for Alembic to detect it.

#### 2. Load DATABASE_URL from .env

```python
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
```

#### 3. Fix SQLModel AutoString Issue

The `render_item()` function is crucial - it converts SQLModel's `AutoString` to standard SQLAlchemy `String`:

```python
def render_item(type_, obj, autogen_context):
    """Render SQLModel types as standard SQLAlchemy types in migrations."""
    if isinstance(type_, AutoString):
        # Preserve length if specified
        if type_.length:
            return f"sa.String(length={type_.length})"
        return "sa.String()"
    return False
```

Without this function, migrations will fail with:
```
NameError: name 'sqlmodel' is not defined
```

## Creating Migrations

### Autogenerate Migration

Alembic can automatically detect model changes and generate migrations:

```bash
alembic revision --autogenerate -m "Add user and role tables"
```

This:
1. Compares your models with the current database schema
2. Detects differences (new tables, columns, indexes, etc.)
3. Generates a migration file in `alembic/versions/`

### Example Migration File

```python
"""Add user and role tables

Revision ID: 08c2098ca4f9
Revises:
Create Date: 2025-12-06 19:04:32.123456
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = '08c2098ca4f9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - apply changes"""
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)


def downgrade() -> None:
    """Downgrade schema - revert changes"""
    op.drop_index(op.f('ix_role_name'), table_name='role')
    op.drop_table('role')
```

### Migration File Structure

- `upgrade()`: Apply the changes (forward migration)
- `downgrade()`: Revert the changes (rollback)
- `revision`: Unique identifier for this migration
- `down_revision`: Parent migration (forms a chain)

## Applying Migrations

### Upgrade to Latest

Apply all pending migrations:

```bash
alembic upgrade head
```

Output:
```
INFO  [alembic.runtime.migration] Running upgrade -> 08c2098ca4f9, Add user table
INFO  [alembic.runtime.migration] Running upgrade 08c2098ca4f9 -> 6404ead5fcfb, Add all models
```

### Upgrade to Specific Revision

```bash
alembic upgrade <revision_id>
```

### Downgrade

Revert the last migration:

```bash
alembic downgrade -1
```

Revert to specific revision:

```bash
alembic downgrade <revision_id>
```

Revert all migrations:

```bash
alembic downgrade base
```

## Checking Migration Status

### Current Revision

```bash
alembic current
```

Output:
```
6404ead5fcfb (head)
```

### Migration History

```bash
alembic history
```

Output:
```
08c2098ca4f9 -> 6404ead5fcfb (head), Add all models
<base> -> 08c2098ca4f9, Add user table
```

### View Specific Migration

```bash
alembic show <revision_id>
```

## Common Workflow

### 1. Create New Model

```python
# app/modules/payments/models.py
from sqlmodel import Field
from app.core.mixins import AuditMixin

class Payment(AuditMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    order_id: int = Field(foreign_key="order.id")
```

### 2. Add to Central Imports

```python
# app/models.py
from app.modules.payments.models import Payment  # Add this

__all__ = [
    "User", "Role", ..., "Payment"  # Add to __all__
]
```

### 3. Generate Migration

```bash
alembic revision --autogenerate -m "Add payment table"
```

### 4. Review Migration

Open the generated file in `alembic/versions/` and verify the changes.

### 5. Apply Migration

```bash
alembic upgrade head
```

## Manual Migrations

Sometimes you need to write migrations manually:

```bash
# Create empty migration
alembic revision -m "add payment status index"
```

Edit the generated file:

```python
def upgrade() -> None:
    op.create_index('ix_payment_status', 'payment', ['status'])


def downgrade() -> None:
    op.drop_index('ix_payment_status', table_name='payment')
```

## Common Operations

### Adding a Column

```python
def upgrade() -> None:
    op.add_column('user', sa.Column('phone', sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column('user', 'phone')
```

### Modifying a Column

```python
def upgrade() -> None:
    op.alter_column('product', 'price',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(10, 2),
                    existing_nullable=False)

def downgrade() -> None:
    op.alter_column('product', 'price',
                    existing_type=sa.Numeric(10, 2),
                    type_=sa.Float(),
                    existing_nullable=False)
```

### Adding an Index

```python
def upgrade() -> None:
    op.create_index('ix_order_customer_date', 'order', ['customer_id', 'created_at'])

def downgrade() -> None:
    op.drop_index('ix_order_customer_date', table_name='order')
```

### Creating an Enum Type (PostgreSQL)

```python
def upgrade() -> None:
    op.execute("CREATE TYPE orderstatus AS ENUM ('PENDING', 'CONFIRMED', 'SHIPPED')")
    op.add_column('order', sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'SHIPPED', name='orderstatus')))

def downgrade() -> None:
    op.drop_column('order', 'status')
    op.execute("DROP TYPE orderstatus")
```

## Troubleshooting

### Issue 1: AutoString Not Defined

**Error:**
```python
NameError: name 'sqlmodel' is not defined
```

**Solution:** Add `render_item()` function to `alembic/env.py` (see configuration above).

### Issue 2: Models Not Detected

**Error:** Migration is empty even though you added models.

**Solution:** Ensure model is imported in `app/models.py`:

```python
# app/models.py
from app.modules.new_module.models import NewModel  # Add this

__all__ = [..., "NewModel"]  # Add to __all__
```

### Issue 3: Circular Import Dependencies

**Warning:**
```
SAWarning: Cannot correctly sort tables; there are unresolvable cycles between tables "branch, role, user"
```

**Explanation:** This is normal when using `AuditMixin` with self-referencing foreign keys (`created_by_id`, etc.). Alembic handles this correctly.

### Issue 4: Migration Conflicts

**Error:** Multiple head revisions exist.

**Solution:** Merge heads:

```bash
alembic merge heads -m "merge multiple heads"
```

### Issue 5: Database Out of Sync

**Error:** Migration fails because database doesn't match expected state.

**Solution:** Stamp the database with the correct revision:

```bash
# Mark database as being at specific revision (without running migrations)
alembic stamp head
```

**Warning:** Only use this if you manually fixed the database or know it matches the revision.

## Best Practices

### 1. Always Review Auto-Generated Migrations

Autogenerate is smart but not perfect. Always review before applying:

```bash
# Generate
alembic revision --autogenerate -m "add something"

# Review the file in alembic/versions/

# Then apply
alembic upgrade head
```

### 2. Use Descriptive Migration Messages

```bash
# Good
alembic revision --autogenerate -m "Add payment table with stripe integration"

# Bad
alembic revision --autogenerate -m "update"
```

### 3. Test Migrations Locally First

Always test on development database before production:

```bash
# Apply
alembic upgrade head

# Test your app

# Rollback to test downgrade works
alembic downgrade -1

# Reapply
alembic upgrade head
```

### 4. Never Edit Applied Migrations

Once a migration is applied (especially in production), never edit it. Create a new migration instead.

### 5. Backup Before Major Migrations

```bash
# PostgreSQL backup
pg_dump -U postgres tecno_rev_db > backup.sql

# Then run migration
alembic upgrade head
```

### 6. Use Transactions

Alembic uses transactions by default. If a migration fails, changes are rolled back.

For PostgreSQL, DDL is transactional (great!). For MySQL, it's not (be careful).

## Production Deployment

### Deploy Process

1. **Backup database**
2. **Pull new code with migrations**
3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```
4. **Restart application**

### Automated Deployment

Include in your deployment script:

```bash
#!/bin/bash
set -e  # Exit on error

echo "Pulling latest code..."
git pull origin main

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Running migrations..."
alembic upgrade head

echo "Restarting application..."
systemctl restart tecno-rev-api

echo "Deployment complete!"
```

## Next Steps

You now have a complete understanding of:
- Installing and configuring Alembic with SQLModel
- Creating and applying migrations
- Managing database schema changes safely

Continue to:
- **API Endpoints** - Building REST endpoints with routers
- **Authentication** - Implementing JWT and role-based access
- **Best Practices** - Production-ready patterns
