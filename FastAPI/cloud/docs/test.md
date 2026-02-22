
## Comprehensive Testing Checklist for Your FastAPI Project

Here's a complete list of things to try out and verify your implementation:

---

## 🚀 Part 1: Quick Start & Server Health

### 1. Start the Server
```bash
cd /Users/Mac/code/project/FastAPI
python -m uvicorn main:app --reload
```
**Expected**: Server starts on `http://localhost:8000`

### 2. Check Health Endpoint
```bash
curl http://localhost:8000/health
```
**Expected**: `{"status":"healthy","timestamp":"..."}`

### 3. Access Interactive API Docs
- Open browser: `http://localhost:8000/docs` (Swagger UI)
- Open browser: `http://localhost:8000/redoc` (ReDoc)

**Expected**: Full API documentation with all endpoints visible

---

## 🔐 Part 2: Authentication Flow (via Swagger UI)

### 4. Register a New User
**In Swagger UI:**
1. Find `POST /auth/register`
2. Click "Try it out"
3. Use this JSON:
```json
{
  "email": "test@example.com",
  "password": "testpass123"
}
```
4. Execute

**Expected**: `201 Created` with user details

### 5. Try Duplicate Registration (Should Fail)
- Use same email again
**Expected**: `400 Bad Request` - "Email already registered"

### 6. Login to Get Token
**In Swagger UI:**
1. Find `POST /auth/login`
2. Use form data:
   - `username`: `test@example.com`
   - `password`: `testpass123`
3. Execute

**Expected**: `200 OK` with `access_token`

### 7. Authorize in Swagger UI
1. Copy the `access_token` from login response
2. Click green "Authorize" button at top
3. Paste token in "Value" field (without "Bearer")
4. Click "Authorize"

**Expected**: Lock icons turn locked 🔒

### 8. Get Current User Info
**In Swagger UI:**
1. Find `GET /auth/me`
2. Execute

**Expected**: Your user details returned

---

## 📝 Part 3: Todo CRUD Operations (via Swagger UI)

### 9. Create Your First Todo
**In Swagger UI:**
1. Find `POST /todos`
2. Use this JSON:
```json
{
  "title": "Learn FastAPI",
  "ddl": "2026-02-25 18:00"
}
```
3. Execute

**Expected**: `201 Created` with todo details + background email task logged

### 10. Create Multiple Todos
Create these todos:
```json
{"title": "Buy groceries", "ddl": "2026-02-21 10:00"}
{"title": "Finish homework", "ddl": "2026-02-22 15:00"}
{"title": "Call mom"}
```

**Expected**: All created successfully

### 11. List All Todos
**In Swagger UI:**
1. Find `GET /todos`
2. Try different parameters:
   - `skip=0, limit=10`
   - `filter_today=true`
   - `filter_week=true`
   - `title=Learn`
   - `sort_by=ddl, sort_order=desc`

**Expected**: Paginated results with filtering/sorting working

### 12. Get Single Todo
1. Find `GET /todos/{id}`
2. Use `id=1`

**Expected**: Single todo details

### 13. Update a Todo
1. Find `PATCH /todos/{id}`
2. Use `id=1` with JSON:
```json
{
  "done": true,
  "title": "Learn FastAPI - COMPLETED!"
}
```

**Expected**: Todo updated successfully

### 14. Delete a Todo
1. Find `DELETE /todos/{id}`
2. Use `id=1`

**Expected**: `204 No Content`

---

## ⚡ Part 4: Performance Monitoring

### 15. Check Request Timing Headers
**In browser DevTools or curl:**
```bash
curl -i http://localhost:8000/health
```

**Expected**: Response headers include `X-Request-Duration: 0.0023s`

### 16. Trigger Slow Query Warning
**In Swagger UI:**
1. Create 50+ todos quickly
2. List all with `GET /todos?limit=100`

**Check terminal logs for:**
- `INFO: Request timing | GET /todos | Duration: X.XXXXs`
- Possibly `WARNING: SLOW QUERY DETECTED` if query > 0.1s

### 17. Monitor Server Logs
**Watch for:**
- Request timing logs for every endpoint
- Background task execution logs
- Database query timing (if slow)

---

## 🧪 Part 5: Run Automated Tests

### 18. Run All Tests
```bash
cd /Users/Mac/code/project/FastAPI
pytest tests/ -v
```

**Expected**: All tests pass (60+ tests)

### 19. Run Tests with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

**Expected**: Coverage report generated in `htmlcov/index.html`

### 20. Open Coverage Report
```bash
open htmlcov/index.html
```

**Expected**: >80% coverage across all modules

### 21. Run Specific Test Suites
```bash
# Test authentication
pytest tests/test_api.py::TestAuthAPI -v

# Test CRUD operations
pytest tests/test_crud.py -v

# Test middleware
pytest tests/test_timing_middleware.py -v

# Test slow query logging
pytest tests/test_slow_query_logging.py -v

# Test health check
pytest tests/test_health_check.py -v
```

---

## 🔒 Part 6: Security & Rate Limiting

### 22. Test Rate Limiting
**In terminal (rapid requests):**
```bash
for i in {1..25}; do curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user$i@test.com\",\"password\":\"pass123\"}"; done
```

**Expected**: After 20 requests/minute, get `429 Too Many Requests`

### 23. Test Invalid Token
**In Swagger UI:**
1. Authorize with fake token: `invalid_token_12345`
2. Try `GET /todos`

**Expected**: `401 Unauthorized`

### 24. Test Missing Token
**In curl:**
```bash
curl http://localhost:8000/todos
```

**Expected**: `403 Forbidden`

---

## 🗄️ Part 7: Database & Migrations

### 25. Check Database File
```bash
ls -lh /Users/Mac/code/project/FastAPI/todos.db
```

**Expected**: Database file exists with size > 0

### 26. View Migration History
```bash
cd /Users/Mac/code/project/FastAPI
alembic history
```

**Expected**: List of migrations including "Add indexes for performance"

### 27. Check Current Migration
```bash
alembic current
```

**Expected**: Shows latest migration applied

### 28. Verify Database Indexes
**In Python shell:**
```bash
python
```
```python
from sqlalchemy import inspect
from db import engine

inspector = inspect(engine)
indexes = inspector.get_indexes('todos')
for idx in indexes:
    print(f"{idx['name']}: {idx['column_names']}")
```

**Expected**: See indexes on `owner_id`, `ddl`, `done`, `title`, and composite `(owner_id, ddl)`

---

## 🎯 Part 8: Edge Cases & Error Handling

### 29. Test Invalid Date Format
**In Swagger UI:**
```json
{
  "title": "Bad date test",
  "ddl": "invalid-date"
}
```

**Expected**: Todo created with default ddl (tomorrow 9pm)

### 30. Test User Isolation
1. Register second user: `user2@test.com`
2. Login as user2
3. Try `GET /todos`

**Expected**: Empty list (can't see user1's todos)

### 31. Test Accessing Other User's Todo
1. Login as user2
2. Try `GET /todos/1` (user1's todo)

**Expected**: `404 Not Found`

### 32. Test Transaction Rollback
**In Swagger UI:**
1. Find `POST /debug/tx-fail`
2. Execute

**Expected**: `400 Bad Request` + no todo created in database

### 33. Test Transaction Atomicity
**In Swagger UI:**
1. Find `POST /debug/tx-atomic`
2. Execute

**Expected**: `400 Bad Request` + no todos created (both rolled back)

---

## 📊 Part 9: Background Tasks

### 34. Monitor Background Task Logs
**After creating a todo, check logs for:**
```
INFO: Sending email to test@example.com
INFO: Email sent successfully
```

**Expected**: Email simulation logged

---

## 🌐 Part 10: API Documentation

### 35. Explore Swagger UI Features
- Try "Schemas" section at bottom
- Check request/response examples
- Test "Download" OpenAPI spec button

### 36. Test ReDoc
- Open `http://localhost:8000/redoc`
- Navigate through sections
- Check search functionality

---

## 📝 Part 11: Final Verification Checklist

Run through this quick checklist:

- [ ] Server starts without errors
- [ ] Health check returns 200
- [ ] Can register new user
- [ ] Can login and get token
- [ ] Can create todos
- [ ] Can list todos with pagination
- [ ] Can filter todos (today/week/title)
- [ ] Can sort todos (ddl/title, asc/desc)
- [ ] Can update todos
- [ ] Can delete todos
- [ ] Request timing headers present
- [ ] Slow query logging works
- [ ] All tests pass (60+ tests)
- [ ] Coverage > 80%
- [ ] Rate limiting works
- [ ] User isolation works
- [ ] Database indexes created
- [ ] Migrations applied
- [x] Background tasks execute
- [ ] API docs accessible

---

## 🎓 Bonus: Advanced Testing

### 37. Load Testing (Optional)
```bash
# Install Apache Bench
brew install httpd

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health
```

**Expected**: See requests/second, timing percentiles

### 38. Database Query Analysis
```bash
# Enable SQLAlchemy query logging
export SQLALCHEMY_ECHO=1
python -m uvicorn main:app --reload
```

**Expected**: See all SQL queries in terminal

---

## 📋 Summary

You now have **38 comprehensive tests** covering:
- ✅ Authentication & Authorization
- ✅ CRUD Operations
- ✅ Pagination & Filtering
- ✅ Performance Monitoring
- ✅ Database Optimization
- ✅ Error Handling
- ✅ Security Features
- ✅ Background Tasks
- ✅ API Documentation

**Start with Parts 1-3** (basic functionality), then explore the rest!