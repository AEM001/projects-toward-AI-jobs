# Day 6 Practical Guide: API Testing + Postman Collection

## 🎯 Today's Goals
- Configure pytest testing environment
- Write complete API endpoint tests
- Create test database
- Implement test coverage analysis
- Create Postman test collection

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation Before Starting (30 minutes)

### 1. Read Learning Materials
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Official Documentation](https://docs.pytest.org/)
- [httpx Documentation](https://www.python-httpx.org/)

### 2. Understand Testing Concepts

#### Test Types
- **Unit Tests** - Test individual functions/methods
- **Integration Tests** - Test interactions between multiple components
- **End-to-End Tests** - Test complete user flows

#### Testing Pyramid
```
       /\
      /E2E\      ← Few end-to-end tests
     /------\
    /Integration\  ← Moderate integration tests
   /----------\
  /  Unit Tests  \  ← Many unit tests
 /--------------\
```

---

## 🛠️ Practical Steps

### Step 1: Configure Test Environment (30 minutes) ⭐ Core


**Code Explanation**:
1. **In-memory database** - Use SQLite in-memory database for fast and isolated testing
2. **scope="function"** - Each test function has an independent database
3. **fixture** - pytest's dependency injection mechanism
4. **TestClient** - Test client provided by FastAPI

### Step 2: Write API Endpoint Tests (60 minutes) ⭐ Core


### Step 3: Run Tests (20 minutes)

```bash
# 1. Run all tests
pytest tests/ -v

# 2. Run specific test file
pytest tests/test_todos_api.py -v

# 3. Run specific test class
pytest tests/test_todos_api.py::TestCreateTodo -v

# 4. Run specific test method
pytest tests/test_todos_api.py::TestCreateTodo::test_create_todo_success -v

# 5. View test coverage
pytest tests/ --cov=src --cov-report=html

# 6. View detailed coverage report
open htmlcov/index.html  # macOS
```

### Step 4: Create Postman Test Collection (30 minutes)


---

## ✅ Today's Results Checklist

### File List
- [x] `tests/conftest.py` - pytest configuration
- [x] `tests/test_todos_api.py` - API tests
- [x] `docs/postman_collection.json` - Postman collection

### Function Verification
```bash
# 1. Run all tests
pytest tests/ -v

# 2. View coverage
pytest tests/ --cov=src --cov-report=term-missing

# 3. Import Postman collection
# Open Postman → Import → Select postman_collection.json
```

### Learning Achievements
- [x] Mastered pytest testing framework
- [x] Learned to write API tests
- [x] Understood test coverage
- [x] Learned to use Postman
- [x] Mastered testing best practices

---

## 📝 Today's Summary

On Day 6, you completed:
1. ✅ Configured test environment
2. ✅ Wrote complete API tests
3. ✅ Implemented test coverage analysis
4. ✅ Created Postman test collection
5. ✅ Mastered testing best practices

**Tomorrow's Preview (Day 7)**:
- Improve project documentation
- Optimize code structure
- Prepare for deployment
- Project summary

---

**Congratulations on completing Day 6! Testing coverage complete!** 🎉
