# Day 4 Practical Guide: Enhance CRUD API + Advanced Features

## 🎯 Today's Goals
- Complete all CRUD operations
- Implement advanced query features (search, sorting)
- Add batch operations
- Optimize API response format
- Implement task statistics functionality

**Estimated Time**: 2-3 hours  
**Difficulty**: ⭐⭐⭐ (Intermediate)

---

## 📚 Preparations Before Starting (30 minutes)

### 1. Read Learning Materials
- [RESTful API Design Best Practices](https://restfulapi.net/)
- [SQLAlchemy Advanced Queries](https://docs.sqlalchemy.org/en/20/orm/queryguide/)
- [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)

### 2. Understand RESTful API Design Principles

#### HTTP Method Semantics
| Method | Purpose | Idempotent | Safe |
|------|------|--------|--------|
| GET | Get resource | ✅ | ✅ |
| POST | Create resource | ❌ | ❌ |
| PUT | Complete update | ✅ | ❌ |
| PATCH | Partial update | ❌ | ❌ |
| DELETE | Delete resource | ✅ | ❌ |

#### HTTP Status Codes
- **200 OK** - Success
- **201 Created** - Creation successful
- **204 No Content** - Deletion successful (no return content)
- **400 Bad Request** - Request error
- **404 Not Found** - Resource not found
- **422 Unprocessable Entity** - Validation failed

---

## 🛠️ Practical Steps

### Step 1: Extend Schema (30 minutes)


### Step 2: Extend Service Layer (40 minutes) ⭐ Core


### Step 3: Update Routes (40 minutes) ⭐ Core


### Step 4: Test Advanced Features (30 minutes)

```bash
# 1. Create test data
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Python","priority":"high"}'

curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn FastAPI","priority":"medium"}'

# 2. Test search
curl "http://localhost:8000/todos?search=Python"

# 3. Test sorting
curl "http://localhost:8000/todos?sort_by=priority&sort_order=desc"

# 4. Test pagination
curl "http://localhost:8000/todos?page=1&page_size=5"

# 5. Test statistics
curl "http://localhost:8000/todos/stats"

# 6. Test batch delete
curl -X POST "http://localhost:8000/todos/batch-delete" \
  -H "Content-Type: application/json" \
  -d '{"ids":[1,2,3]}'

# 7. Delete completed tasks
curl -X DELETE "http://localhost:8000/todos/completed/all"
```

---

## ✅ Today's Results Check

### Feature Verification
- [x] Search function works
- [x] Sorting function works
- [x] Pagination function works
- [x] Statistics function works
- [x] Batch delete function works
- [x] Swagger documentation complete

### Learning Outcomes
- [x] Mastered advanced queries (search, sorting)
- [x] Learned to implement pagination
- [x] Understood batch operations
- [x] Mastered statistical queries
- [x] Learned to use tags to organize APIs

---

## 💡 Common Questions

### Q1: Why paginate?
**A**: Avoid returning too much data at once, improve performance and user experience.

### Q2: What's the difference between ilike and like?
**A**: `ilike` is case-insensitive fuzzy query, `like` is case-sensitive.

### Q3: How to optimize search performance?
**A**: Add indexes to search fields, use full-text search engines (like Elasticsearch).

---

## 📝 Today's Summary

On Day 4, you completed:
1. ✅ Implemented search functionality
2. ✅ Implemented sorting functionality
3. ✅ Implemented pagination functionality
4. ✅ Implemented statistics functionality
5. ✅ Implemented batch operations

**Tomorrow's Preview (Day 5)**:
- Improve exception handling
- Add logging system
- Implement data validation
- Optimize code structure

---

**Congratulations on completing Day 4! The API functionality is already very comprehensive!** 🎉
