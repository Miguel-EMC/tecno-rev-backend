# TecnoRev Backend - E-commerce API

A complete RESTful API for an e-commerce platform built with FastAPI, SQLModel, and PostgreSQL.

## Features

- ✅ **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (5 user roles)
  - Email/password login
  - Protected routes

- ✅ **User Management**
  - User registration and profiles
  - Role assignment (SUPER_ADMIN, BRANCH_MANAGER, SALES_AGENT, LOGISTICS, CUSTOMER)
  - Soft delete with audit tracking

- 🚧 **Product Catalog** *(In Progress)*
  - Categories and products
  - Product images
  - Price management

- 🚧 **Inventory Management** *(In Progress)*
  - Multi-branch stock tracking
  - Inventory movements
  - Stock entries

- 🚧 **Sales** *(In Progress)*
  - Order management
  - Order items
  - Discount coupons

- 🚧 **Logistics** *(In Progress)*
  - Shipment tracking
  - Delivery management

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases with Python type annotations
- **PostgreSQL** - Powerful relational database
- **bcrypt** - Password hashing
- **python-jose** - JWT token generation and validation
- **Alembic** - Database migrations
- **uv** - Fast Python package manager

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- uv (Python package manager)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd tecno-rev-backend
```

### 2. Create virtual environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Setup PostgreSQL

Create a PostgreSQL database:

```bash
createdb tecno_rev_db
```

### 5. Configure environment variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/tecno_rev_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Generate a secure SECRET_KEY:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Run migrations

```bash
alembic upgrade head
```

### 7. Seed roles

```bash
python scripts/seed_roles_final.py
```

This creates 5 roles in the database:
- SUPER_ADMIN (ID: 1)
- BRANCH_MANAGER (ID: 2)
- SALES_AGENT (ID: 3)
- LOGISTICS (ID: 4)
- CUSTOMER (ID: 5)

### 8. Start the server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication

| Method | Endpoint              | Description           | Auth Required |
|--------|-----------------------|-----------------------|---------------|
| POST   | /api/auth/register    | Register new user     | No            |
| POST   | /api/auth/token       | Login (get JWT)       | No            |
| GET    | /api/auth/profile     | Get current user      | Yes           |
| PATCH  | /api/auth/profile     | Update profile        | Yes           |

### Example Usage

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": 1234567890
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

**Get Profile:**
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer <your-token>"
```

## Project Structure

```
tecno-rev-backend/
├── app/
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── mixins.py          # Reusable model mixins
│   ├── modules/
│   │   ├── auth/              # Authentication module
│   │   │   ├── models.py      # User and Role models
│   │   │   ├── schema.py      # Pydantic schemas
│   │   │   ├── service.py     # Business logic
│   │   │   ├── router.py      # API routes
│   │   │   └── enums.py       # Role enums
│   │   ├── catalog/           # Product catalog
│   │   ├── inventory/         # Inventory management
│   │   ├── sales/             # Sales and orders
│   │   └── logistics/         # Shipping and logistics
│   └── models.py              # Central model imports
├── docs/                      # Documentation
├── scripts/
│   └── seed_roles_final.py   # Seed initial roles
├── alembic/                   # Database migrations
├── .env                       # Environment variables
├── requirements.txt           # Project dependencies
└── README.md
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

1. [Installation & Setup](./docs/01-installation.md)
2. [Database Setup](./docs/02-database-setup.md)
3. [Project Architecture](./docs/03-architecture.md)
4. [Models & Relationships](./docs/04-models-relationships.md)
5. [Database Migrations](./docs/05-migrations.md)
6. [Authentication Schemas](./docs/06-auth-schemas.md)
7. [Authentication Services](./docs/07-auth-services.md)
8. [Authentication Routes](./docs/08-auth-routes.md)
9. [Authentication Examples](./docs/09-auth-examples.md)
10. [CRUD Pattern](./docs/10-crud-pattern.md)
11. [Roles Setup](./docs/11-roles-setup.md)
12. [JWT Tokens](./docs/12-jwt-tokens.md)

## User Roles

The system supports 5 user roles with different permission levels:

| Role            | ID | Description                                    |
|-----------------|----|-------------------------------------------------|
| SUPER_ADMIN     | 1  | Full system access, manages all branches       |
| BRANCH_MANAGER  | 2  | Manages specific branch and its inventory      |
| SALES_AGENT     | 3  | Processes sales at POS                         |
| LOGISTICS       | 4  | Handles shipping and package preparation       |
| CUSTOMER        | 5  | Web/mobile customers (default role)            |

See [Roles Setup Documentation](./docs/11-roles-setup.md) for detailed role descriptions.

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Code Style

We use:
- **Ruff** for linting
- **Black** for code formatting
- **mypy** for type checking

## Security

- Passwords are hashed using bcrypt
- JWT tokens for stateless authentication
- Role-based access control (RBAC)
- Soft delete for data integrity
- Audit fields (created_at, updated_at, created_by, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[MIT License](LICENSE)

## Support

For questions or issues, please open an issue on GitHub.
