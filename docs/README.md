# Building a RESTful API with FastAPI - Complete Guide

This documentation provides a comprehensive guide to building a scalable RESTful API using FastAPI, SQLModel, PostgreSQL, and modern Python tools.

## Table of Contents

1. [Installation & Setup](./01-installation.md)
   - Installing FastAPI with uv
   - Project initialization
   - Development environment setup

2. [Database Setup](./02-database-setup.md)
   - PostgreSQL configuration
   - Database connection with SQLModel
   - Environment variables management

3. [Project Architecture](./03-architecture.md)
   - Folder structure
   - Module organization
   - Design patterns and best practices

4. [Models & Relationships](./04-models-relationships.md)
   - Creating SQLModel models
   - One-to-One relationships
   - One-to-Many relationships
   - Many-to-Many relationships
   - Audit mixins and soft delete

5. [Database Migrations](./05-migrations.md)
   - Alembic setup
   - Creating migrations
   - Running migrations
   - Common issues and solutions

6. [Authentication Schemas](./06-auth-schemas.md)
   - Creating request/response schemas
   - Pydantic validation
   - Email validation with EmailStr
   - Password and field constraints
   - Testing schemas

7. [Authentication Services](./07-auth-services.md)
   - Password hashing with bcrypt
   - JWT token creation and validation
   - User authentication
   - CRUD operations
   - Current user dependencies

8. [Authentication Routes](./08-auth-routes.md)
   - Creating API endpoints
   - OAuth2 password flow
   - Register, login, profile endpoints
   - Dependency injection
   - Testing with FastAPI docs

9. [Authentication Examples](./09-auth-examples.md)
   - Complete Python examples
   - cURL commands
   - JavaScript/Fetch API
   - React/Axios integration
   - Error handling
   - Token expiration handling

10. [CRUD Pattern with Protected Routes](./10-crud-pattern.md)
   - Standard CRUD operations
   - Schema-Service-Router pattern
   - Protected vs public routes
   - Route authentication
   - Module-specific validations
   - Complete examples for all modules

11. [Roles Setup & Permissions](./11-roles-setup.md)
   - User roles overview (SUPER_ADMIN, BRANCH_MANAGER, SALES_AGENT, LOGISTICS, CUSTOMER)
   - Role descriptions and capabilities
   - Initial setup and seeding roles
   - Role assignment during registration
   - Role-based access control (RBAC)
   - Common scenarios and troubleshooting

12. [JWT Tokens - How Authentication Works](./12-jwt-tokens.md)
   - JWT overview and structure
   - Token generation and verification
   - Token storage (localStorage, cookies, etc.)
   - Security best practices
   - Common issues and solutions
   - Future enhancements (refresh tokens, blacklist)

13. [Best Practices](./13-best-practices.md) *(Coming soon)*
   - Error handling
   - Logging
   - Testing
   - Performance optimization

## About This Project

This is a complete e-commerce backend system featuring:

- **User Management**: Authentication, roles, and permissions
- **Product Catalog**: Categories, products, and images
- **Inventory Management**: Stock tracking, movements, and multi-branch support
- **Sales**: Orders, order items, and coupons
- **Logistics**: Shipments and delivery tracking

## Technology Stack

- **FastAPI**: Modern, fast web framework
- **SQLModel**: SQL databases in Python with type safety
- **PostgreSQL**: Reliable and powerful database
- **Alembic**: Database migration tool
- **uv**: Fast Python package installer
- **Docker**: Containerization (optional)

## Getting Started

Start with [Installation & Setup](./01-installation.md) to begin building your API.
