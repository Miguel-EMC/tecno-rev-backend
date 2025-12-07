# Database Setup with PostgreSQL and SQLModel

This guide covers setting up PostgreSQL and connecting it to your FastAPI application using SQLModel, with Alembic for database migrations.

## Installing PostgreSQL

### Using Docker (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: tecno-rev-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tecno_rev_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Start the database:

```bash
docker-compose up -d
```

### Verify PostgreSQL is Running

```bash
# Check container status
docker ps

# Access PostgreSQL shell
docker exec -it tecno-rev-db psql -U postgres -d tecno_rev_db
```

## Environment Configuration

Create a `.env` file in your project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tecno_rev_db
```

**Important:** Add `.env` to your `.gitignore` to avoid committing sensitive data.

## Database Connection with SQLModel

Create `app/core/database.py`:

```python
from sqlmodel import Session, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
```

### Key Components Explained

1. **`load_dotenv()`**: Loads environment variables from `.env` file
2. **`create_engine()`**: Creates SQLAlchemy engine for database connection
3. **`echo=True`**: Enables SQL query logging (useful for development)
4. **`get_session()`**: Generator function that provides database sessions (used as FastAPI dependency)

## Install Required Dependencies

```bash
uv add sqlmodel
uv add psycopg2-binary
uv add python-dotenv
```

## Why We Use Alembic (Not SQLModel.metadata.create_all)

Instead of using `SQLModel.metadata.create_all(engine)` directly, we use **Alembic** for database migrations because:

1. **Version Control**: Track database schema changes over time
2. **Migration History**: Know exactly what changed and when
3. **Rollback Capability**: Revert changes if needed
4. **Team Collaboration**: Share database changes with your team
5. **Production Safety**: Apply changes incrementally and safely

### The Difference

**❌ Don't do this (Direct creation):**
```python
# This recreates tables on every restart - BAD for production
SQLModel.metadata.create_all(engine)
```

**✅ Do this instead (Alembic migrations):**
```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migration
alembic upgrade head
```

## Database Connection in Practice

The `get_session()` function is used as a FastAPI dependency:

```python
from fastapi import FastAPI, Depends
from sqlmodel import Session
from app.core.database import get_session

app = FastAPI()

@app.get("/users")
def get_users(session: Session = Depends(get_session)):
    # Session is automatically provided by FastAPI
    users = session.exec(select(User)).all()
    return users
```

FastAPI automatically:
1. Calls `get_session()` before the endpoint
2. Provides the session to your function
3. Closes the session after the response

## Connection Configuration

### Development Settings

```python
engine = create_engine(
    DATABASE_URL,
    echo=True  # Show SQL queries in console
)
```

### Production Settings

```python
engine = create_engine(
    DATABASE_URL,
    echo=False,           # Disable SQL logging
    pool_size=10,         # Connection pool size
    max_overflow=20,      # Max connections beyond pool_size
    pool_pre_ping=True,   # Test connections before using
    pool_recycle=3600     # Recycle connections after 1 hour
)
```

## Testing Database Connection

Create a simple health check endpoint in `app/main.py`:

```python
from fastapi import FastAPI, Depends
from sqlmodel import Session, text
from app.core.database import get_session

app = FastAPI()

@app.get("/health/db")
def check_database(session: Session = Depends(get_session)):
    """Check if database connection is working"""
    try:
        result = session.exec(text("SELECT 1")).first()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

Run the app and visit http://localhost:8000/health/db

## Common Issues

### Issue 1: Connection Refused

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**
- Check if PostgreSQL is running: `docker ps`
- Verify port 5432 is not blocked
- Check DATABASE_URL format

### Issue 2: Database Does Not Exist

```
FATAL: database "tecno_rev_db" does not exist
```

**Solution:**
```bash
docker exec -it tecno-rev-db psql -U postgres -c "CREATE DATABASE tecno_rev_db;"
```

### Issue 3: Authentication Failed

```
FATAL: password authentication failed for user "postgres"
```

**Solution:** Check username and password in your `.env` file match docker-compose.yml

## Security Best Practices

1. **Never commit `.env`** - Add to `.gitignore`
2. **Use strong passwords** in production
3. **Use environment-specific URLs**:
   ```env
   # Development
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tecno_dev

   # Production
   DATABASE_URL=postgresql://prod_user:strong_password@prod-host:5432/tecno_prod
   ```
4. **Enable SSL in production**:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

## Next Steps

Now that your database is connected, continue to:
- [Project Architecture](./03-architecture.md) - Learn how to structure your code
- [Models & Relationships](./04-models-relationships.md) - Create database models
- [Database Migrations](./05-migrations.md) - Use Alembic for schema changes
