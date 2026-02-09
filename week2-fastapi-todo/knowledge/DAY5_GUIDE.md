# Day 5 Practical Guide: Exception Handling + Logging System + Data Validation

## 🎯 Today's Goals

- Implement unified exception handling
- Add complete logging system
- Enhance data validation
- Add request/response middleware
- Implement API rate limiting (optional)

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

- [FastAPI Exception Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Python logging module](https://docs.python.org/3/library/logging.html)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)

---

## 🛠️ Practical Steps

### Step 1: Create Custom Exceptions (30 minutes) ⭐ Core


### Step 2: Add Logging System (40 minutes) ⭐ Core


### Step 3: Add Request Logging Middleware (30 minutes)


### Step 4: Enhance Data Validation (30 minutes)


### Step 5: Update main.py to Integrate All Features (40 minutes) ⭐ Core


---

## ✅ Today's Results Check

### File Checklist

- [x] `src/utils/exceptions.py` - Custom exceptions
- [x] `src/utils/logger.py` - Logging system
- [x] `src/utils/middleware.py` - Middleware
- [x] Updated `src/main.py` - Integrate all features
- [x] `logs/app.log` - Log file (auto-generated)

### Function Verification

```bash
# 1. Start application, observe logs
uvicorn src.main:app --reload

# 2. Test normal requests (check logs)
curl "http://localhost:8000/todos"

# 3. Test validation errors
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"<invalid>"}'

# 4. Test 404 errors
curl "http://localhost:8000/todos/999"

# 5. View log file
cat logs/app.log
```

### Learning Outcomes

- [x] Master custom exceptions
- [x] Learn to configure logging system
- [x] Understand middleware mechanism
- [x] Master global exception handling
- [x] Learn to enhance data validation

---

## 📝 Today's Summary

On Day 5, you completed:

1. ✅ Implemented unified exception handling
2. ✅ Added complete logging system
3. ✅ Implemented request logging middleware
4. ✅ Enhanced data validation
5. ✅ Improved code robustness

**Tomorrow's Preview (Day 6)**:

- Write complete API tests
- Create Postman test collections
- Run test coverage analysis

---

**Congratulations on completing Day 5! The application is now very robust!** 🎉
