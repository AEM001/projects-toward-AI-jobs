# Day 3 Practical Guide: SQLite + SQLAlchemy ORM

## 🎯 Today's Goals

- Understand ORM (Object-Relational Mapping) concepts
- Configure SQLAlchemy database connection
- Create database models (ORM Model)
- Implement database session management
- Migrate from in-memory storage to SQLite

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

- [SQLAlchemy Official Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [FastAPI SQL Databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLite Basics](https://www.sqlite.org/docs.html)

### 2. Understand Core Concepts

#### What is ORM?

- **ORM (Object-Relational Mapping)** - Object-Relational Mapping
- Represent database tables with Python classes
- Use object operations instead of SQL statements
- Automatic data type conversion

#### SQLAlchemy Architecture

```
Application Layer (FastAPI)
    ↓
ORM Layer (SQLAlchemy Models)
    ↓
Core Layer (SQL Expression)
    ↓
Database (SQLite)
```

#### Schema vs Model (Important!)

- **Pydantic Schema**: Data validation and serialization at API layer
- **SQLAlchemy Model**: Table structure definition at database layer

```
API Request → Pydantic Schema → Business Logic → SQLAlchemy Model → Database
```

---

## 🛠️ Practical Steps

### Step 1: Configure Database Connection (30 minutes) ⭐ Core



**Code Explanation**:

1. **create_engine** - Create database engine
2. **sessionmaker** - Create session factory
3. **get_db** - Dependency injection function, automatically manages session lifecycle
4. **init_db** - Create all database tables

### Step 2: Create ORM Models (40 minutes) ⭐ Core


**Code Explanation**:

1. **__tablename__** - Specify table name
2. **Column** - Define columns
3. **primary_key** - Primary key
4. **index** - Create index, speed up queries
5. **nullable** - Whether NULL is allowed
6. **server_default** - Database-level default value
7. **func.now()** - Use database's current time function
8. **onupdate** - Automatically update timestamp on update


### Step 3: Create Database Service Layer (40 minutes) ⭐ Core


**Code Explanation**:

1. **Static methods** - Use `@staticmethod`, no need to instantiate
2. **db.add()** - Add object to session
3. **db.commit()** - Commit transaction
4. **db.refresh()** - Refresh object to get database-generated values
5. **db.query()** - Create query
6. **filter()** - Add filter conditions
7. **first()** - Get first record
8. **all()** - Get all records
9. **count()** - Get record count

### Step 4: Update main.py to Use Database (40 minutes) ⭐ Core


**Code Explanation**:

1. **Depends(get_db)** - Dependency injection, automatically manages database session
2. **startup_event** - Initialize database on application startup
3. **TodoService** - Use service layer to handle business logic
4. **Separation of concerns** - Route layer only handles HTTP, business logic in service layer

### Step 5: Test Database Functionality (20 minutes)

```bash
# 1. Start application (will automatically create database)
uvicorn src.main:app --reload

# 2. Create Todo
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn SQLAlchemy",
    "description": "Complete ORM tutorial",
    "priority": "high"
  }'

# 3. Get all Todos
curl "http://localhost:8000/todos"

# 4. Update Todo
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# 5. View database file
ls -lh todo.db

# 6. Use SQLite command line to view data
sqlite3 todo.db "SELECT * FROM todos;"
```

---

## ✅ Today's Achievements Check

### File Checklist

- [x] `src/database/base.py` - Base model
- [x] `src/database/connection.py` - Database connection
- [x] `src/models/todo.py` - ORM model
- [x] `src/services/todo_service.py` - Business logic
- [x] Updated `src/main.py` - API using database
- [x] `todo.db` - SQLite database file (auto-generated)

### Function Verification

```bash
# 1. Start application
uvicorn src.main:app --reload

# 2. Create data
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test database","priority":"high"}'

# 3. Restart application, data should still be there
# Ctrl+C to stop, then restart
uvicorn src.main:app --reload

# 4. Get data again
curl "http://localhost:8000/todos"
```

### Learning Outcomes

- [x] Understand ORM concepts
- [x] Learn to configure SQLAlchemy
- [x] Master creating ORM models
- [x] Learn to use dependency injection to manage database sessions
- [x] Understand service layer pattern
- [x] Master basic SQLAlchemy queries

---

## 💡 Common Questions

### Q1: What's the difference between ORM and writing SQL directly?

**A**: ORM uses object operations, safer and easier to maintain. Direct SQL is more flexible but error-prone.

### Q2: Why use dependency injection?

**A**: Automatically manages resource lifecycle, ensures database sessions are properly closed, avoids memory leaks.

### Q3: Where is the database file?

**A**: The `todo.db` file in the project root directory.

### Q4: How to view generated SQL?

**A**: Set `echo=True` in `create_engine`.

### Q5: How to reset the database?

**A**: Delete the `todo.db` file, restarting the application will automatically recreate it.

---

## 📝 Today's Summary

In Day 3, you completed:

1. ✅ Configured SQLAlchemy database connection
2. ✅ Created ORM models
3. ✅ Implemented service layer
4. ✅ Learned dependency injection
5. ✅ Implemented data persistence

**Tomorrow's Preview (Day 4)**:

- Complete all CRUD operations
- Optimize query performance
- Add more business logic
- Implement advanced filtering features

---

## 🎯 Homework (Optional)

1. **Add Indexes**: Add indexes for frequently queried fields
2. **Add Relationships**: Learn SQLAlchemy relationship mapping (one-to-many, many-to-many)
3. **View Database**: Use SQLite Browser to view database structure
4. **Performance Testing**: Create 1000 records, test query performance

---

**Congratulations on completing Day 3! Database integration complete!** 🎉
