# Installation & Setup

This guide walks you through setting up a FastAPI project using `uv`, a fast Python package installer and resolver.

## Prerequisites

- Python 3.12 or higher
- Git
- PostgreSQL 14+ (for database)

## Installing uv

`uv` is a blazingly fast Python package installer and resolver written in Rust.

### On macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### On Windows

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify installation

```bash
uv --version
```

## Creating a New Project

### 1. Initialize the project

```bash
mkdir tecno-rev-backend
cd tecno-rev-backend
```

### 2. Initialize uv project

```bash
uv init
```

This creates:
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version specification

### 3. Install FastAPI and dependencies

```bash
# Core dependencies
uv add fastapi
uv add "uvicorn[standard]"
uv add sqlmodel
uv add psycopg2-binary
uv add python-dotenv
uv add alembic

# Development dependencies
uv add --dev pytest
uv add --dev httpx
uv add --dev ruff
```

### 4. Your `pyproject.toml` should look like this:

```toml
[project]
name = "tecno-rev-backend"
version = "0.1.0"
description = "E-commerce RESTful API with FastAPI"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.6",
    "uvicorn[standard]>=0.34.0",
    "sqlmodel>=0.0.22",
    "psycopg2-binary>=2.9.10",
    "python-dotenv>=1.0.1",
    "alembic>=1.14.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.4",
    "httpx>=0.28.1",
    "ruff>=0.8.4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Project Structure (Initial)

Create the initial folder structure:

```bash
mkdir -p app/{core,modules,api}
touch app/__init__.py
touch app/main.py
touch .env
touch .gitignore
```

Your structure should look like:

```
tecno-rev-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   ├── modules/
│   └── api/
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── .python-version
```

## Create `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
.venv/
venv/

# FastAPI
*.db
*.sqlite3

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# uv
uv.lock
```

## Basic FastAPI Application

Create `app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Tecno-Rev Backend",
    description="E-commerce RESTful API",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Tecno-Rev API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

## Running the Application

### Using uv

```bash
uv run uvicorn app.main:app --reload
```

### Traditional method (after activating venv)

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn app.main:app --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Advantages of Using uv

1. **Speed**: 10-100x faster than pip
2. **Deterministic**: Lock file ensures reproducible installs
3. **Dependency Resolution**: Better conflict resolution
4. **Simple**: One tool for virtual envs and packages
5. **Modern**: Built for modern Python workflows

## Next Steps

Continue to [Database Setup](./02-database-setup.md) to configure PostgreSQL and database connections.

## Common Commands Reference

```bash
# Add a package
uv add package-name

# Add dev dependency
uv add --dev package-name

# Run a command in the virtual environment
uv run command

# Sync dependencies from lock file
uv sync

# Update dependencies
uv lock --upgrade

# Remove a package
uv remove package-name
```
