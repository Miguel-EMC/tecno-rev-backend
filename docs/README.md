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

6. [API Endpoints](./06-api-endpoints.md) *(Coming soon)*
   - Router setup
   - CRUD operations
   - Request/Response schemas
   - Validation

7. [Authentication & Authorization](./07-authentication.md) *(Coming soon)*
   - JWT tokens
   - Password hashing
   - Role-based access control

8. [Best Practices](./08-best-practices.md) *(Coming soon)*
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
