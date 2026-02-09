# Day 1 Practical Guide: FastAPI Basics + Project Initialization

## 🎯 Today's Goals

- Understand core FastAPI framework concepts
- Set up a complete project directory structure
- Create your first FastAPI application
- Implement basic API endpoints
- Access automatically generated Swagger documentation

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐ (Beginner)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

Quickly browse the following documents (focus on examples):

- [FastAPI Official Tutorial - First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

### 2. Understand FastAPI Core Concepts

#### What is FastAPI?

- Modern, high-performance Web framework
- Based on Python 3.6+ type hints
- Automatically generated API documentation (Swagger UI)
- Automatic data validation (Pydantic)
- Supports asynchronous programming

#### FastAPI vs Flask

| Feature           | FastAPI                           | Flask                 |
| ----------------- | --------------------------------- | --------------------- |
| Performance       | Very fast (comparable to Node.js) | Slower                |
| Data Validation   | Automatic (Pydantic)              | Manual                |
| API Documentation | Auto-generated                    | Requires plugins      |
| Type Hints        | Mandatory                         | Optional              |
| Async Support     | Native support                    | Requires extra config |

### 3. Understand Project Structure

```
week2-fastapi-todo/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── main.py              # Today's focus!
│   ├── models/              # Database models (Tomorrow)
│   ├── schemas/             # Pydantic models (Tomorrow)
│   ├── routers/             # API routes
│   ├── services/            # Business logic
│   ├── database/            # Database configuration
│   └── utils/               # Utility functions
├── tests/
├── .env
├── requirements.txt
└── README.md
```

---

## 🛠️ Practical Steps

### Step 1: Create Project Directory (10 minutes)

```bash
# 1. Enter project directory
cd /Users/Mac/code/project/week2-fastapi-todo

# 2. Create all __init__.py files
touch config/__init__.py
touch src/__init__.py
touch src/models/__init__.py
touch src/schemas/__init__.py
touch src/routers/__init__.py
touch src/services/__init__.py
touch src/database/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py

# 3. Verify directory structure
tree -L 2
```

### Step 2: Configure Virtual Environment and Dependencies (10 minutes)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import fastapi; print(fastapi.__version__)"
```

### Step 3: Create First FastAPI App (30 minutes) ⭐ Core

Create `src/main.py` file:

```python
"""
FastAPI TODO API Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application instance
app = FastAPI(
    title="TODO API",
    description="A simple TODO management API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI path
    redoc_url="/redoc"  # ReDoc path
)

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production should restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root path - Health check
@app.get("/")
async def root():
    """
    Root path - API Health check
    """
    return {
        "message": "Welcome to TODO API",
        "status": "healthy",
        "version": "1.0.0"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok"}


# Temporary in-memory storage (will be replaced by database later)
todos_db = []
todo_id_counter = 1


# Get all TODOs
@app.get("/todos")
async def get_todos():
    """
    Get all TODO tasks
    """
    return {"todos": todos_db, "count": len(todos_db)}


# Get single TODO
@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """
    Get a single TODO task by ID

    - **todo_id**: Unique identifier for the TODO task
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo
    return {"error": "Todo not found"}, 404


# Create TODO (Simplified version, will use Pydantic tomorrow)
@app.post("/todos")
async def create_todo(title: str, priority: str = "medium"):
    """
    Create a new TODO task

    - **title**: Task title
    - **priority**: Priority (low, medium, high)
    """
    global todo_id_counter

    new_todo = {
        "id": todo_id_counter,
        "title": title,
        "priority": priority,
        "status": "pending"
    }

    todos_db.append(new_todo)
    todo_id_counter += 1

    return new_todo


# Delete TODO
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """
    Delete a specific TODO task

    - **todo_id**: ID of the TODO task to delete
    """
    global todos_db

    for i, todo in enumerate(todos_db):
        if todo["id"] == todo_id:
            deleted_todo = todos_db.pop(i)
            return {"message": "Todo deleted", "todo": deleted_todo}

    return {"error": "Todo not found"}, 404


# App startup event
@app.on_event("startup")
async def startup_event():
    """
    Executed when the application starts
    """
    print("🚀 FastAPI Application started successfully!")
    print("📖 Visit http://localhost:8000/docs to view API documentation")


# App shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Executed when the application shuts down
    """
    print("👋 FastAPI Application closed")
```

**Code Explanation**:

1. **FastAPI Instance** - Create application, configure metadata
2. **CORS Middleware** - Allow cross-origin requests
3. **Route Decorators** - `@app.get()`, `@app.post()`, `@app.delete()`
4. **Path Parameters** - `{todo_id}` auto-parsing and validation
5. **Query Parameters** - Function parameters automatically become query parameters
6. **Async Functions** - Use `async def` (can also use regular `def`)
7. **Lifecycle Events** - `startup` and `shutdown` events

### Step 4: Start Application (10 minutes)

```bash
# Start development server (auto-reload)
uvicorn src.main:app --reload

# Specify port
uvicorn src.main:app --reload --port 8000

# Specify host (allow external access)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
🚀 FastAPI Application started successfully!
📖 Visit http://localhost:8000/docs to view API documentation
INFO:     Application startup complete.
```

### Step 5: Test API (30 minutes) ⭐ Core

#### Method 1: Use Swagger UI (Recommended)

1. Open browser and visit: `http://localhost:8000/docs`
2. You will see auto-generated interactive API documentation
3. Click any endpoint, click "Try it out"
4. Fill in parameters, click "Execute"
5. View response results

#### Method 2: Use curl

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Create TODO
curl -X POST "http://localhost:8000/todos?title=LearnFastAPI&priority=high"

# 3. Get all TODOs
curl http://localhost:8000/todos

# 4. Get single TODO
curl http://localhost:8000/todos/1

# 5. Delete TODO
curl -X DELETE http://localhost:8000/todos/1
```

#### Method 3: Use Python requests

Create test script `test_manual.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# Create TODO
response = requests.post(
    f"{BASE_URL}/todos",
    params={"title": "Learn FastAPI", "priority": "high"}
)
print("Create TODO:", response.json())

# Get all TODOs
response = requests.get(f"{BASE_URL}/todos")
print("All TODOs:", response.json())

# Get single TODO
response = requests.get(f"{BASE_URL}/todos/1")
print("Single TODO:", response.json())

# Delete TODO
response = requests.delete(f"{BASE_URL}/todos/1")
print("Delete TODO:", response.json())
```

Run test:

```bash
python test_manual.py
```

### Step 6: Explore API Documentation (20 minutes)

#### Swagger UI (`/docs`)

- Interactive API documentation
- Can test API directly
- View request/response models
- View parameter descriptions

#### ReDoc (`/redoc`)

- More aesthetic documentation display
- Suitable for reading and sharing
- Cannot test directly

#### OpenAPI Schema (`/openapi.json`)

- Raw OpenAPI specification
- Can be imported into Postman
- Can generate client code

### Step 7: Add Configuration Management (20 minutes)

Create `config/settings.py`:

```python
"""
Application Configuration Management
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings class
    """
    # Application info
    app_name: str = "FastAPI TODO API"
    app_version: str = "1.0.0"
    debug: bool = True

    # API configuration
    api_prefix: str = "/api/v1"

    # CORS configuration
    cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
```

Update `src/main.py` to use settings:

```python
from config.settings import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    # ... other configs
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # ... other configs
)
```

Create `.env` file:

```bash
cp .env.example .env
```

---

## ✅ Today's Accomplishments

### File Checklist

- [x] Complete project directory structure
- [x] `requirements.txt` - Dependency list
- [x] `.gitignore` - Git ignore configuration
- [x] `.env.example` and `.env` - Environment variables
- [x] `src/main.py` - FastAPI application (approx. 120 lines)
- [x] `config/settings.py` - Configuration management

### Functionality Verification

```bash
# 1. Start application
uvicorn src.main:app --reload

# 2. Access documentation
# Open browser: http://localhost:8000/docs

# 3. Test API
curl http://localhost:8000/
curl -X POST "http://localhost:8000/todos?title=Test&priority=high"
curl http://localhost:8000/todos
```

### Learning Outcomes

- [x] Understand FastAPI framework basics
- [x] Learn to create FastAPI applications
- [x] Master route decorators usage
- [x] Understand path parameters and query parameters
- [x] Learn to test API using Swagger UI
- [x] Understand CORS configuration
- [x] Learn to use Pydantic Settings

---

## 💡 Frequently Asked Questions

### Q1: What is the difference between FastAPI and Flask?

**A**: FastAPI is more modern, has higher performance, automatically generates documentation, and handles data validation automatically. Flask is simpler and has a more mature ecosystem.

### Q2: Why use async def?

**A**: Supports asynchronous programming to improve concurrency performance. Beginners can use regular `def` initially, as the effect is similar.

### Q3: What is Swagger UI?

**A**: An automatically generated interactive API documentation that allows you to test APIs directly in the browser.

### Q4: How to change the port?

**A**: `uvicorn src.main:app --reload --port 8080`

### Q5: Why can't I access /docs?

**A**: 

1. Confirm application is running
2. Check if the port is correct
3. Ensure no firewall is blocking access

---

## 📝 Today's Summary

In Day 1, you completed:

1. ✅ Set up FastAPI project structure
2. ✅ Created first FastAPI application
3. ✅ Implemented basic CRUD endpoints
4. ✅ Learned to use Swagger UI
5. ✅ Configured CORS and environment variables

**Coming Tomorrow (Day 2)**:

- Learning Pydantic data validation
- Creating request/response models
- Implementing complete data validation
- Optimizing API endpoints

---

## 🎯 Homework (Optional)

1. **Add update endpoint**: Implement `PUT /todos/{id}` to update tasks
2. **Add query parameter**: Support filtering by status `GET /todos?status=pending`
3. **Custom response**: Return more user-friendly error messages
4. **Explore documentation**: Read first 5 chapters of official FastAPI tutorial

---

**Congratulations on completing Day 1! Tomorrow we will learn Pydantic data validation!** 🎉
