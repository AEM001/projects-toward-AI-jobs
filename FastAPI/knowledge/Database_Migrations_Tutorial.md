# Day 4-5: Database Migrations with Alembic

A comprehensive tutorial for learning database migrations from scratch.

---

## Table of Contents

1. [What is a Database Migration?](#what-is-a-database-migration)
2. [Why Use Alembic?](#why-use-alembic)
3. [Installation](#installation)
4. [Project Structure Setup](#project-structure-setup)
5. [Understanding Alembic Components](#understanding-alembic-components)
6. [Your First Migration](#your-first-migration)
7. [Migration Operations](#migration-operations)
8. [The Migration Workflow](#the-migration-workflow)
9. [Auto-Generating Migrations](#auto-generating-migrations)
10. [Handling Common Scenarios](#handling-common-scenarios)
11. [Advanced Topics](#advanced-topics)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)
14. [Cheat Sheet](#cheat-sheet)
15. [Exercises](#exercises)

---

## What is a Database Migration?

A **database migration** is a systematic way of managing changes to your database schema over time. Think of it as "version control for your database."

### The Problem Without Migrations

```sql
-- Version 1: Simple users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT
);

-- Version 2: Need to add email
-- What do you do?
DROP TABLE users;  -- LOSES ALL DATA!
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT
);
```

### The Migration Solution

```sql
-- Migration 1: Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT
);

-- Migration 2: Add email column (preserves data!)
ALTER TABLE users ADD COLUMN email TEXT;
```

Migrations let you:
- **Preserve data** when schema changes
- **Roll back** changes if something breaks
- **Track history** of database changes
- **Collaborate** with other developers seamlessly

---

## Why Use Alembic?

### Popular Alternatives

| Tool | Language | Pros | Cons |
|------|----------|------|------|
| **Alembic** | Python | Works with SQLAlchemy, very flexible | Python-focused |
| Flyway | Java/Java | Simple, great CI/CD integration | SQL-based only |
| Django Migrations | Python | Built into Django | Django-specific |
| Prisma Migrate | TypeScript | Type-safe, great DX | Node.js ecosystem |

### Why Alembic?

1. **Native SQLAlchemy integration** - Seamless with your ORM
2. **Python-based** - Use Python logic in migrations
3. **Extremely flexible** - Manual control when needed
4. **Great tooling** - Auto-generate migrations from models
5. **Branching support** - Handle complex schemas

---

## Installation

### Step 1: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Alembic and Dependencies

```bash
pip install alembic
pip install sqlalchemy  # Alembic requires SQLAlchemy
pip install psycopg2-binary  # For PostgreSQL (optional)
pip install pymysql  # For MySQL (optional)
```

### Step 3: Verify Installation

```bash
alembic --version
# Should output: 1.13.1 or similar
```

---

## Project Structure Setup

### Step 1: Create a Demo Project Structure

```bash
mkdir -p alembic_tutorial/{app,alembic/versions}
cd alembic_tutorial
tree
```

Expected structure:
```
alembic_tutorial/
├── alembic/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── models.py
│   └── database.py
├── alembic.ini
└── venv/
```

### Step 2: Create app/__init__.py

```python
# app/__init__.py
"""Main application package."""
```

### Step 3: Create app/database.py

This file sets up the database connection and base class.

```python
# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Choose your database
# SQLite (simple, no setup):
DATABASE_URL = "sqlite:///./tutorial.db"

# PostgreSQL (production):
# DATABASE_URL = "postgresql://user:password@localhost/mydb"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Print all SQL statements (great for learning!)
    connect_args={"check_same_thread": False}  # SQLite only
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session (for use with FastAPI/Flask)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Step 4: Create app/models.py

Define your database models using SQLAlchemy.

```python
# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """User model for demonstration."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"
```

### Step 5: Create alembic.ini

```bash
alembic init alembic
```

Edit `alembic.ini`:

```ini
# alembic.ini
# A generic, single-line configuration.

[alembic]
# Path to the migration scripts
script_path = alembic

# Template for generated scripts
script_template = %(script)s/script.py.mako

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers = console
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Important: Add your database URL**

```ini
[alembic]
# This is REQUIRED - points to your database
sqlalchemy.url = sqlite:///./tutorial.db

# Other settings...
script_path = alembic
```

For PostgreSQL:
```ini
sqlalchemy.url = postgresql://username:password@localhost/mydatabase
```

---

## Understanding Alembic Components

### Directory Structure

```
alembic/
├── env.py           # Migration environment configuration
├── README          # Documentation (can be ignored)
├── script.py.mako  # Template for new migration files
└── versions/       # Directory containing all migration files
    ├── 001_initial_migration.py
    ├── 002_add_user_table.py
    └── 003_add_email_index.py
```

### env.py - The Heart of Alembic

This file controls how migrations run.

```python
# alembic/env.py
import sys
import os

# Add your app to path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine
from alembic import context

# Import your app's database setup
from app.database import Base
from app.models import User, Todo  # Import all your models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Key configuration points:**

| Setting | Purpose |
|---------|---------|
| `target_metadata` | Points to your models for auto-generation |
| `run_migrations_offline()` | Used for read-only migrations |
| `run_migrations_online()` | Used for live database connections |

### script.py.mako - Migration Template

This is the template used when creating new migrations.

```python
# alembic/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision || 'head'}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
```

---

## Your First Migration

### Step 1: Create Initial Migration Manually

```python
# alembic/versions/001_initial_users.py
"""Create users table

Revision ID: 001
Revises:
Create Date: 2024-01-15 10:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )

    # Create an index on username for faster lookups
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])


def downgrade():
    # Drop in reverse order
    op.drop_index('ix_users_email')
    op.drop_index('ix_users_username')
    op.drop_table('users')
```

### Step 2: Understand the Migration Structure

```python
# Metadata header
revision = '001'           # Unique ID for this revision
down_revision = None        # Parent revision (None = first migration)
branch_labels = None        # For branching (advanced)
depends_on = None           # Dependencies (rarely used)

def upgrade():
    """
    Called when applying migration
    - Create tables
    - Add columns
    - Create indexes
    - Modify data
    """

def downgrade():
    """
    Called when rolling back
    - Must reverse everything from upgrade()
    - Drop tables
    - Drop columns
    - Drop indexes
    - Delete data
    """
```

### Step 3: Apply the Migration

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic] Context class Context: OfflineDirectManager
INFO  [alembic] Running Revision 001: Create users table (preparing)
INFO  [alembic] Running upgrade  -> 001, Create users table
```

### Step 4: Verify It Worked

```python
# Python script to check
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print("Tables:", inspector.get_table_names())
print("\nUsers columns:")
for column in inspector.get_columns('users'):
    print(f"  - {column['name']}: {column['type']}")
```

---

## Migration Operations

Alembic provides `op` functions for all common database operations.

### Creating Tables

```python
def upgrade():
    # Create a simple table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),  # Unique constraint
    )

    # Create table with foreign key
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            ondelete='CASCADE'  # Options: CASCADE, RESTRICT, SET NULL
        )
    )


def downgrade():
    op.drop_table('posts')
    op.drop_table('users')
```

### Adding/Modifying Columns

```python
def upgrade():
    # Add a new column
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))

    # Add column with default value
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true'))

    # Add column with not null and default
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))


def downgrade():
    # Drop column (reverse of add)
    op.drop_column('users', 'phone')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
```

### Modifying Column Attributes

```python
def upgrade():
    # Change column type (requires different syntax)
    op.alter_column('users', 'email', type_=sa.String(200))

    # Make column nullable
    op.alter_column('users', 'phone', nullable=True)

    # Make column NOT nullable
    op.alter_column('users', 'username', nullable=False)

    # Rename column
    op.alter_column('users', 'old_name', new_column_name='new_name')


def downgrade():
    # Reverse the changes
    op.alter_column('users', 'email', type_=sa.String(100))
    # ... other reversals
```

### Creating/Dropping Indexes

```python
def upgrade():
    # Create simple index
    op.create_index('ix_users_email', 'users', ['email'])

    # Create composite index
    op.create_index('ix_posts_user_created', 'posts', ['user_id', 'created_at'])

    # Create unique index
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade():
    op.drop_index('ix_users_email')
    op.drop_index('ix_posts_user_created')
    op.drop_constraint('uq_users_username', 'users')
```

### Creating/Dropping Constraints

```python
def upgrade():
    # Add foreign key to existing column
    op.create_foreign_key(
        'fk_posts_user',      # Constraint name
        'posts',              # Table
        'users',              # Referenced table
        ['user_id'],          # Local columns
        ['id'],               # Referenced columns
        ondelete='CASCADE'
    )

    # Add check constraint
    op.create_check_constraint(
        'chk_age_positive',
        'users',
        'age >= 0'
    )


def downgrade():
    op.drop_constraint('fk_posts_user', 'posts')
    op.drop_constraint('chk_age_positive', 'users')
```

### Data Manipulation

```python
def upgrade():
    # Insert data
    op.execute("""
        INSERT INTO users (username, email, hashed_password)
        VALUES ('admin', 'admin@example.com', 'hashed_password')
    """)

    # Update data
    op.execute("""
        UPDATE users SET role = 'admin' WHERE username = 'admin'
    """)


def downgrade():
    # Delete the inserted data
    op.execute("DELETE FROM users WHERE username = 'admin'")
```

### Renaming Things

```python
def upgrade():
    # Rename table
    op.rename_table('users', 'accounts')

    # Rename column
    op.alter_column('posts', 'old_title', new_column_name='title')


def downgrade():
    op.rename_table('accounts', 'users')
    op.alter_column('posts', 'title', new_column_name='old_title')
```

---

## The Migration Workflow

### Complete Workflow Diagram

```
1. Create models in app/models.py
           ↓
2. Auto-generate or create migration
           ↓
3. Review migration (very important!)
           ↓
4. Apply migration: alembic upgrade head
           ↓
5. Test application works
           ↓
[If something goes wrong]
           ↓
6. Rollback: alembic downgrade -1
           ↓
7. Fix models, create new migration
           ↓
8. Repeat from step 3
```

### Creating New Migrations

#### Method 1: Manual Creation

```bash
alembic revision -m "description_of_change"
```

This creates an empty migration file you fill in yourself.

#### Method 2: Auto-Generation (Recommended)

```bash
alembic revision --autogenerate -m "description_of_change"
```

Alembic compares your current models to the database and generates appropriate changes.

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2
alembic upgrade -2  # Note: no, downgrade uses different command

# Upgrade to specific revision
alembic upgrade 003

# Show what would be applied (dry run)
alembic upgrade head --sql > upgrade.sql
cat upgrade.sql
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback two migrations
alembic downgrade -2

# Rollback to specific revision
alembic downgrade 002

# Rollback all migrations (back to initial state)
alembic downgrade base
```

### Checking Migration Status

```bash
# Show current revision
alembic current
# Output: 001 (or the current head revision)

# Show migration history
alembic history
# Output:
# 001 -> 002 (add_email) [head]
# 002 -> 003 (add_posts) [current]

# Show pending migrations
alembic heads
# Shows the current head revision(s)

# Show detailed history with revision IDs
alembic history --verbose
```

### Visualizing Migrations

```bash
# Generate a graph
alembic history --indicate-current
```

```
→ 001 (initial)
  |
  v
→ 002 (add_email)
  |
  v
→ 003 (add_posts) [current]
```

---

## Auto-Generating Migrations

### How Auto-Generation Works

```mermaid
graph TD
    A[Your Models] --> B[Alembic compares]
    C[Current Database Schema] --> B
    B --> D[Diff detected]
    D --> E[Generate migration]
    E --> F[Manual review needed!]
```

### Example: Adding a New Model

**1. Update your models.py:**

```python
# app/models.py (updated)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


# NEW: Add Todo model
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
```

**2. Generate migration:**

```bash
alembic revision --autogenerate -m "add_todos_table"
```

**3. Review the generated migration:**

```python
# alembic/versions/004_add_todos_table.py
"""add_todos table

Revision ID: 004
Revises: 003
Create Date: 2024-01-15 12:00:00

"""

from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_todos_id', 'todos', ['id'])


def downgrade():
    op.drop_index('ix_todos_id')
    op.drop_table('todos')
```

**4. Apply the migration:**

```bash
alembic upgrade head
```

### Example: Modifying an Existing Table

**1. Update your model:**

```python
# In app/models.py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # ADDED: New column
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
```

**2. Generate and review:**

```bash
alembic revision --autogenerate -m "add_user_profile_fields"
```

**3. Generated migration (review it!):**

```python
def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')
```

### What Auto-Generation Detects

| Change | Auto-Detected? |
|--------|---------------|
| New table | ✓ Yes |
| Drop table | ✓ Yes |
| New column | ✓ Yes |
| Drop column | ✓ Yes |
| Column type change | ✓ Yes |
| Column nullable change | ✓ Yes |
| New index | ✓ Yes |
| New foreign key | ✓ Yes |
| Table rename | ✗ No (needs manual) |
| Column rename | ✗ No (needs manual) |
| Complex data changes | ✗ No (needs manual) |

### Important: Always Review Auto-Generated Migrations!

```bash
# Step 1: Generate
alembic revision --autogenerate -m "your_message"

# Step 2: READ THE FILE
cat alembic/versions/*.py | less

# Step 3: Verify it's correct
# If wrong, delete and create manually or edit it

# Step 4: Apply
alembic upgrade head
```

---

## Handling Common Scenarios

### Scenario 1: Adding a Column with Default Value

**The Challenge:** Adding a NOT NULL column to an existing table.

**Solution:**

```python
def upgrade():
    # Step 1: Add column as nullable
    op.add_column('users', sa.Column('role', sa.String(20), nullable=True))

    # Step 2: Update existing rows with default value
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")

    # Step 3: Alter to NOT NULL
    op.alter_column('users', 'role', nullable=False)


def downgrade():
    op.alter_column('users', 'role', nullable=True)
    op.drop_column('users', 'role')
```

### Scenario 2: Renaming a Column

```python
def upgrade():
    op.alter_column('users', 'old_name', new_column_name='new_name')


def downgrade():
    op.alter_column('users', 'new_name', new_column_name='old_name')
```

### Scenario 3: Renaming a Table

```python
def upgrade():
    op.rename_table('users', 'accounts')


def downgrade():
    op.rename_table('accounts', 'users')
```

### Scenario 4: Changing Column Type (PostgreSQL Example)

```python
def upgrade():
    # PostgreSQL-specific type change
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(200)")


def downgrade():
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(100)")
```

### Scenario 5: Adding an Enum Type (PostgreSQL)

```python
def upgrade():
    # Create enum type
    op.execute("CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator')")

    # Add column with enum type
    op.add_column('users', sa.Column('role', sa.Enum('user_role', name='user_role'), nullable=True))


def downgrade():
    op.drop_column('users', 'role')
    op.execute("DROP TYPE user_role")
```

### Scenario 6: Complex Data Migration

```python
def upgrade():
    # Normalize email to lowercase
    op.execute("UPDATE users SET email = LOWER(email)")

    # Remove duplicates
    op.execute("""
        DELETE FROM users
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM users
            GROUP BY email
        )
    """)


def downgrade():
    # This can't be easily reversed
    # Consider documenting this limitation
    pass
```

### Scenario 7: Adding a Unique Constraint

```python
def upgrade():
    # Create unique constraint with name
    op.create_unique_constraint('uq_users_username', 'users', ['username'])


def downgrade():
    op.drop_constraint('uq_users_username', 'users')
```

### Scenario 8: Multi-Step Schema Changes

When you need to do multiple things at once:

```python
def upgrade():
    # Step 1: Add new column
    op.add_column('users', sa.Column('temp_email', sa.String(100)))

    # Step 2: Copy data
    op.execute("UPDATE users SET temp_email = email")

    # Step 3: Drop old column
    op.drop_column('users', 'email')

    # Step 4: Rename new column
    op.alter_column('users', 'temp_email', new_column_name='email')

    # Step 5: Add unique constraint
    op.create_unique_constraint('uq_users_email', 'users', ['email'])


def downgrade():
    # Reverse in opposite order
    op.drop_constraint('uq_users_email', 'users')
    op.alter_column('users', 'email', new_column_name='temp_email')
    op.add_column('users', sa.Column('email', sa.String(100)))
    op.execute("UPDATE users SET email = temp_email")
    op.drop_column('users', 'temp_email')
```

---

## Advanced Topics

### Branching and Merging

When you have multiple development branches:

```bash
# Check current branches
alembic branches

# Create a branch point
alembic revision -m "branch_point" --branch

# Merge branches
alembic revision -m "merge_branch" --merge-anches <revision1>,<revision2>
```

### Offline Migrations

Run migrations without a live database connection:

```bash
# Generate SQL without applying
alembic upgrade head --sql > migration.sql

# Review the SQL
cat migration.sql

# Apply manually
psql -d mydb -f migration.sql
```

### Environment-Specific Configurations

Modify `env.py` for different environments:

```python
from alembic import context
import os

# Get environment
env = os.getenv('ENV', 'development')

if env == 'production':
    # Production settings
    config.set_main_option('sqlalchemy.url', 'postgresql://...')
    target_metadata = Base.metadata
else:
    # Development settings
    config.set_main_option('sqlalchemy.url', 'sqlite:///./dev.db')
    target_metadata = Base.metadata
```

### Multiple Databases

Handle multiple databases in one project:

```python
# In env.py
from app.database import Base, metadata1, metadata2

# Use specific metadata for each
target_metadata = metadata1  # or metadata2
```

### Custom Migration Functions

Create reusable functions in `env.py`:

```python
def upgrade():
    # Use custom function
    add_timestamp_column('users', 'last_login')
    add_foreign_key_if_not_exists('posts', 'users', 'author_id', 'id')


def add_timestamp_column(table_name, column_name):
    op.add_column(
        table_name,
        sa.Column(column_name, sa.DateTime(), server_default=sa.func.now())
    )


def add_foreign_key_if_not_exists(table, ref_table, local_col, ref_col):
    # Check if FK exists (implementation depends on database)
    pass
```

### UUID Support

```python
import uuid
from sqlalchemy.dialects.postgresql import UUID

def upgrade():
    op.add_column('users', sa.Column('id', UUID(as_uuid=True), primary_key=True))


def downgrade():
    op.drop_column('users', 'id')
```

### Using Context in Migrations

Access configuration in migrations:

```python
def upgrade():
    # Get a configuration value
    table_name = 'users'

    # Use it in operations
    op.add_column(table_name, sa.Column('new_col', sa.String(50)))
```

---

## Best Practices

### 1. Version Control Your Migrations

```bash
# Always commit migrations with code changes
git add alembic/versions/
git commit -m "Add todos table migration"
```

### 2. Use Descriptive Migration Names

```bash
# Good
alembic revision -m "add_user_avatar_url"
alembic revision -m "create_posts_table_with_user_fk"

# Bad
alembic revision -m "update1"
alembic revision -m "fix"
alembic revision -m "change"
```

### 3. Review Before Applying

```python
# ALWAYS review generated migrations
def upgrade():
    # Check for dangerous operations
    op.drop_table('users')  # ⚠️ Dangerous! Did you mean to do this?
```

### 4. Test Downgrade Path

```bash
# Always test that downgrade works
alembic upgrade head           # Apply
# Test your application
alembic downgrade -1           # Rollback
# Test your application again
alembic upgrade head           # Re-apply
```

### 5. Keep Migrations Small

**Bad:**
```python
def upgrade():
    op.create_table('users')
    op.create_table('posts')
    op.create_table('comments')
    op.create_table('likes')
    op.add_column('users', sa.Column('email'))
    # 20 more operations...
```

**Good:**
```python
# Migration 001
def upgrade():
    op.create_table('users')
```

### 6. Use Transactions

Alembic wraps each migration in a transaction automatically. However, if using `executemany=True` or complex operations:

```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('new_col', sa.String(50)))
        batch_op.create_index('idx_new_col', ['new_col'])
```

### 7. Document Breaking Changes

```python
def upgrade():
    """Add new optional columns to users table.

    This migration is backward compatible - no data loss.
    """
    op.add_column('users', sa.Column('new_field', sa.String(100)))
```

### 8. Handle Null Values Carefully

```python
def upgrade():
    # Safe: Add nullable column
    op.add_column('users', sa.Column('optional_field', sa.String(100)))

    # NOT safe: Adding NOT NULL without default
    # op.add_column('users', sa.Column('required_field', sa.String(100), nullable=False))

    # Safe alternative:
    op.add_column('users', sa.Column('required_field', sa.String(100), nullable=True))
    op.execute("UPDATE users SET required_field = 'default'")
    op.alter_column('users', 'required_field', nullable=False)
```

### 9. Naming Conventions

| Object | Convention | Example |
|--------|-----------|---------|
| Migration files | `NNN_description.py` | `001_initial.py` |
| Index names | `ix_table_column` | `ix_users_email` |
| FK constraints | `fk_table_column_ref` | `fk_posts_user_id` |
| Unique constraints | `uq_table_column` | `uq_users_email` |

### 10. Don't Modify Applied Migrations

```python
# NEVER DO THIS after migration is applied:
def upgrade():
    op.drop_table('users')  # Destructive!
```

If you made a mistake, create a **new** migration to fix it.

---

## Troubleshooting

### Problem: "Target database is not up to date"

```bash
# Check current state
alembic current

# If behind, upgrade
alembic upgrade head
```

### Problem: "Can't locate revision ID"

```bash
# Check history
alembic history

# If revision doesn't exist, you may need to stamp
alembic stamp <revision>
```

### Problem: Migration fails with "duplicate column"

```bash
# Check if column already exists
alembic downgrade -1  # Rollback
# Fix the migration
alembic upgrade head  # Re-apply
```

### Problem: Circular dependency between migrations

```python
# Solution: Remove depends_on in the later migration
# or restructure migrations
depends_on = None  # Instead of ['other_revision']
```

### Problem: Auto-generate misses changes

1. Ensure `target_metadata` is set correctly in `env.py`
2. Import all models in `env.py`
3. Ensure migrations are applied before generating new ones

```python
# In env.py - CRITICAL
from app.database import Base
from app.models import User, Todo, Post  # Import ALL models

target_metadata = Base.metadata
```

### Problem: PostgreSQL connection issues

```bash
# Check connection
psql -h localhost -U username -d database

# Verify URL format
postgresql://user:password@host:port/database
```

### Problem: SQLite limitations

Some operations aren't supported in SQLite:
- `ALTER COLUMN`
- `DROP COLUMN` (requires table rebuild)
- Complex `ALTER TABLE` operations

**Solution:** Use table rebuild pattern:

```python
def upgrade():
    # Rename old table
    op.rename_table('users', 'users_old')

    # Create new table with correct schema
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        # ... new schema
    )

    # Copy data
    op.execute("INSERT INTO users (id, email) SELECT id, email FROM users_old")

    # Drop old table
    op.drop_table('users_old')
```

### Problem: "Database is already locked"

```bash
# Close all connections
lsof | grep tutorial.db
kill <PID>
```

Or use SQLite in exclusive mode:
```python
engine = create_engine(DATABASE_URL, connect_args={"isolation_level": "EXCLUSIVE"})
```

### Getting Help

```bash
# Show all commands
alembic --help

# Show command help
alembic upgrade --help
alembic downgrade --help
alembic revision --help
```

---

## Cheat Sheet

### Installation & Setup

```bash
pip install alembic sqlalchemy
alembic init alembic
# Edit alembic.ini with your DATABASE_URL
# Edit alembic/env.py to import your models
```

### Daily Workflow

```bash
# 1. Change your models in app/models.py

# 2. Generate migration
alembic revision --autogenerate -m "your_description"

# 3. Review the generated file
cat alembic/versions/*.py | grep -A 50 "def upgrade"

# 4. Apply migration
alembic upgrade head

# 5. If something goes wrong
alembic downgrade -1
# Fix your model, then repeat from step 2
```

### Essential Commands

| Command | Description |
|---------|-------------|
| `alembic current` | Show current revision |
| `alembic history` | Show full history |
| `alembic heads` | Show available heads |
| `alembic upgrade head` | Apply all migrations |
| `alembic upgrade +1` | Apply one migration |
| `alembic downgrade -1` | Rollback one migration |
| `alembic downgrade base` | Rollback all migrations |
| `alembic revision -m "msg"` | Create empty migration |
| `alembic revision --autogenerate -m "msg"` | Auto-generate migration |
| `alembic stamp head` | Mark migration as applied without running |

### Common Operations

```python
# Create table
op.create_table('name', sa.Column('id', sa.Integer(), nullable=False))

# Drop table
op.drop_table('name')

# Add column
op.add_column('table', sa.Column('name', sa.String(50)))

# Drop column
op.drop_column('table', 'name')

# Rename column
op.alter_column('table', 'old_name', new_column_name='new_name')

# Create index
op.create_index('ix_table_name', 'table', ['column'])

# Drop index
op.drop_index('ix_table_name')

# Create FK
op.create_foreign_key('fk_name', 'child_table', 'parent_table', ['fk_col'], ['pk_col'])

# Drop FK
op.drop_constraint('fk_name', 'child_table')

# Execute raw SQL
op.execute("UPDATE table SET col = 'value'")
```

---

## Exercises

### Exercise 1: Basic Setup (15 min)

1. Create a new directory for your practice project
2. Set up virtual environment
3. Install Alembic and SQLAlchemy
4. Initialize Alembic
5. Configure `alembic.ini` for SQLite
6. Create a simple `User` model
7. Create and apply initial migration

**Expected result:** `users` table exists in your database.

---

### Exercise 2: Adding Tables (20 min)

1. Create a `Post` model with:
   - `id` (Integer, primary key)
   - `title` (String, 200 chars)
   - `content` (Text)
   - `published` (Boolean, default False)
   - `created_at` (DateTime)

2. Generate and apply migration
3. Verify the table was created

**Expected result:** `posts` table exists with all columns.

---

### Exercise 3: Adding Relationships (25 min)

1. Add a `user_id` ForeignKey to Post
2. Add relationship attributes to both models
3. Generate migration
4. Apply and verify

**Expected result:** Posts are linked to users via foreign key.

---

### Exercise 4: Column Modifications (20 min)

1. Add `bio` column to User (Text, nullable)
2. Add `slug` column to Post (String, 220, unique)
3. Generate and apply migrations
4. Rollback one migration
5. Re-apply

**Expected result:** You can add columns without data loss.

---

### Exercise 5: Data Migration (30 min)

1. Add `status` column to Post with default 'draft'
2. Run migration
3. Update all existing posts to 'published'
4. Create new migration to require `status` NOT NULL
5. Test downgrade

**Expected result:** Complex migration with default values works correctly.

---

### Exercise 6: Rollback Practice (15 min)

1. Create table `comments`
2. Apply migration
3. Verify table exists
4. Rollback
5. Verify table is gone
6. Re-apply

**Expected result:** You understand upgrade/downgrade cycle.

---

### Exercise 7: Troubleshooting (30 min)

1. Create a migration that intentionally fails
2. Practice reading error messages
3. Fix the issue
4. Apply successfully

**Common errors to practice:**
- Duplicate column
- Missing dependency
- Syntax errors

---

## Summary

You now have a comprehensive understanding of database migrations with Alembic:

| Topic | Key Takeaway |
|-------|-------------|
| **What** | Migrations = version control for database schema |
| **Why** | Preserve data, enable collaboration, track changes |
| **How** | `alembic revision` + `alembic upgrade` |
| **Best Practice** | Always review, test downgrades, keep migrations small |

**Next steps:**
1. Practice the exercises above
2. Integrate into your FastAPI project
3. Set up CI/CD for automatic migrations
4. Explore Alembic's advanced features as needed

---

*Document Version: 1.0*
*Last Updated: 2024*
*Tutorial for: FastAPI Knowledge Base - Day 4-5*