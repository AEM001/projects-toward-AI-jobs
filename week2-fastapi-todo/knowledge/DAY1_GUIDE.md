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
