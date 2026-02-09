# Day 2 Practical Guide: Pydantic Models + Request Validation

## 🎯 Today's Goals

- Understand Pydantic data validation mechanisms
- Create request and response models (Schemas)
- Implement automatic data validation
- Optimize API endpoint type safety
- Learn Pydantic Field validators

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐ (Beginner)

---

## 📚 Preparation (30 minutes)

### 1. Read Learning Materials

- [Pydantic Official Documentation](https://docs.pydantic.dev/)
- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)

### 2. Understand Pydantic Core Concepts

#### What is Pydantic?

- Python data validation library
- Uses type annotations for data validation
- Automatic data type conversion
- Generates JSON Schema
- Core dependency of FastAPI

#### Schema vs Model

- **Schema**: Pydantic model, used for API requests/responses
- **Model**: SQLAlchemy model, used for database tables

```
Request → Pydantic Schema (validation) → Business Logic → SQLAlchemy Model (database)
Database → SQLAlchemy Model → Pydantic Schema (serialization) → Response
```

---

## 🛠️ Practical Steps

### Step 1: Create Basic Schema (40 minutes) ⭐ Core


**Code Explanation**:

1. **Inheritance Structure** - `TodoBase` → `TodoCreate`/`TodoUpdate`/`TodoResponse`
2. **Field Validators** - `min_length`, `max_length`, `description`, `example`
3. **Optional Fields** - Use `Optional[str]` for optional fields
4. **Enum Enumeration** - Limit selectable values
5. **Config Class** - Configure Pydantic behavior
6. **from_attributes** - Allow creation from ORM objects

### Step 2: Update main.py to Use Schema (40 minutes) ⭐ Core


**Code Explanation**:

1. **response_model** - Specify response model, automatic serialization and validation
2. **status_code** - Specify HTTP status code
3. **HTTPException** - Throw HTTP exception
4. **Query Parameters** - Use `Query()` to add validation and description
5. **model_dump()** - Pydantic v2 method, replaces v1's `dict()`
6. **exclude_unset** - Only include fields set by user

### Step 3: Test Data Validation (30 minutes)

Start the application:

```bash
uvicorn src.main:app --reload
```

#### Test 1: Valid Data

```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete tutorial",
    "priority": "high"
  }'
```

#### Test 2: Title Too Short (should fail)

```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "",
    "priority": "high"
  }'
```

Expected response:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

#### Test 3: Invalid Priority (should fail)

```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test",
    "priority": "urgent"
  }'
```

#### Test 4: Update Task

```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

#### Test 5: Query Parameters

```bash
# Filter by status
curl "http://localhost:8000/todos?status=pending"

# Filter by priority
curl "http://localhost:8000/todos?priority=high"

# Pagination
curl "http://localhost:8000/todos?skip=0&limit=10"
```

### Step 4: Test in Swagger UI (20 minutes)

1. Visit `http://localhost:8000/docs`
2. View auto-generated request/response examples
3. Test each endpoint
4. Observe detailed validation error messages
5. View Schema definitions

---

## ✅ Today's Achievement Checklist

### File Checklist

- [x] `src/schemas/__init__.py`
- [x] `src/schemas/todo.py` - Pydantic Schema (~150 lines)
- [x] Updated `src/main.py` - API using Schema (~180 lines)

### Functionality Verification

```bash
# 1. Start application
uvicorn src.main:app --reload

# 2. Test creation (valid data)
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","priority":"high"}'

# 3. Test validation (invalid data)
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"","priority":"invalid"}'

# 4. Test update
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"status":"done"}'
```

### Learning Outcomes

- [x] Understand Pydantic data validation mechanisms
- [x] Learn to create request/response models
- [x] Master the use of Field validators
- [x] Understand the role of response_model
- [x] Learn to use Query parameter validation
- [x] Master HTTPException exception handling

---

## 💡 Common Questions

### Q1: What's the difference between Schema and Model?

**A**: Schema (Pydantic) is for API validation, Model (SQLAlchemy) is for database.

### Q2: Why separate TodoCreate, TodoUpdate, TodoResponse?

**A**: 

- **TodoCreate**: No need for id and timestamps when creating
- **TodoUpdate**: All fields optional when updating
- **TodoResponse**: Response includes all fields

### Q3: What does ... in Field(...) mean?

**A**: Indicates required field, equivalent to `required=True`.

### Q4: What's the difference between model_dump() and dict()?

**A**: Pydantic v2 uses `model_dump()`, v1 uses `dict()`.

### Q5: How to customize validation logic?

**A**: Use `@field_validator` decorator or `@model_validator`.

---

## 📝 Today's Summary

On Day 2, you completed:

1. ✅ Created complete Pydantic Schema
2. ✅ Implemented automatic data validation
3. ✅ Learned to use Field validators
4. ✅ Mastered response_model
5. ✅ Implemented query parameter validation

**Tomorrow's Preview (Day 3)**:

- Integrate SQLite database
- Learn SQLAlchemy ORM
- Implement data persistence
- Create database models

---

## 🎯 Homework (Optional)

1. **Add Custom Validation**: Use `@field_validator` to validate that title cannot contain special characters
2. **Add More Fields**: Add `due_date` (deadline) field for Todo
3. **Optimize Response**: Create unified response format (including success, data, message)
4. **Explore Pydantic**: Read Pydantic documentation to learn more validators

---

**Congratulations on completing Day 2! Tomorrow we'll integrate the database!** 🎉
