# FastAPI Learning Roadmap
**Goal:** Build a strong API foundation through hands-on project development

---

## 📋 Current Status
- ✅ Basic CRUD operations complete
- ✅ Clean architecture (routes → services → CRUD → DB)
- ✅ Transaction management implemented
- ✅ Pydantic validation working

---

## 🎯 Learning Path (4-6 Weeks)

### **Week 1: Code Quality & Error Handling** (8-10 hours)

#### Day 1-2: Clean Code & Logging (3-4 hours)
- [x] **Fix duplicate function** in `crud.py` line 46
- [x] **Add structured logging** using Python's `logging` module
  - Configure logger with different levels (DEBUG, INFO, ERROR)
  - Add request ID tracking
  - Log all CRUD operations
- [x] **Add input validation**
  - Validate ID parameters (must be positive integers)
  - Add custom validators in Pydantic schemas

#### Day 3-4: Error Handling (3-4 hours)
- [x] **Create custom exception classes**
  - `TodoNotFoundException`
  - `ValidationException`
- [x] **Add global exception handler** middleware
  - Consistent error response format
  - Proper HTTP status codes
  - Error logging
- [x] **Add request validation middleware**
  - Validate content-type headers
  - Add request size limits

#### Day 5-6: API Documentation (2-3 hours)
- [x] **Enhance OpenAPI docs**
  - Add detailed descriptions to all endpoints
  - Add request/response examples
  - Add tags for endpoint grouping
- [x] **Add API versioning** (e.g., `/api/v1/todos`)

---

### **Week 2: Production Features** (10-12 hours)

#### Day 1-3: Pagination & Filtering (4-5 hours)
- [ ] **Add pagination to `/todos` endpoint**
  - Query parameters: `skip`, `limit`
  - Return metadata: `total`, `page`, `page_size`
- [ ] **Add filtering capabilities**
  - Filter by `done` status
  - Search by `title` (partial match)
- [ ] **Add sorting**
  - Sort by `id`, `title`, `done`
  - Support ascending/descending order

#### Day 4-5: Configuration & Environment (3-4 hours)
- [ ] **Create `config.py`** using Pydantic Settings
  - Database URL from environment variables
  - API settings (title, version, debug mode)
  - CORS settings
- [ ] **Add `.env` file support**
  - Install `python-dotenv`
  - Separate dev/prod configurations
- [ ] **Add CORS middleware** (if building frontend)

#### Day 6-7: Rate Limiting & Security (3-4 hours)
- [ ] **Add rate limiting** using `slowapi`
  - Limit requests per IP
  - Different limits for different endpoints
- [ ] **Add security headers**
  - HTTPS redirect in production
  - Security headers middleware
- [ ] **Add request/response validation**

---

### **Week 3: Testing Foundation** (12-15 hours)

#### Day 1-2: Setup Testing Framework (3-4 hours)
- [ ] **Install pytest and dependencies**
  - `pytest`, `pytest-cov`, `httpx`
- [ ] **Create test database setup**
  - Separate test database
  - Fixtures for database session
  - Setup/teardown for each test
- [ ] **Create `tests/` directory structure**
  - `tests/test_crud.py`
  - `tests/test_services.py`
  - `tests/test_api.py`
  - `tests/conftest.py` (shared fixtures)

#### Day 3-5: Write Unit Tests (5-6 hours)
- [ ] **Test CRUD functions** (`test_crud.py`)
  - Test `create_todo`
  - Test `list_todos`
  - Test `get_todo` (found and not found)
  - Test `update_todo`
  - Test `delete_todo`
- [ ] **Test service layer** (`test_services.py`)
  - Test error handling (404 cases)
  - Test business logic

#### Day 6-7: Integration Tests (4-5 hours)
- [ ] **Test API endpoints** (`test_api.py`)
  - Test POST `/todos` (success and validation errors)
  - Test GET `/todos` (empty, with data, pagination)
  - Test GET `/todos/{id}` (found and 404)
  - Test PUT `/todos/{id}` (success, 404, validation)
  - Test DELETE `/todos/{id}` (success and 404)
- [ ] **Add test coverage reporting**
  - Aim for >80% coverage
  - Generate HTML coverage report

---

### **Week 4: Advanced Features** (12-15 hours)

#### Day 1-3: Authentication & Authorization (6-7 hours)
- [ ] **Add User model and database table**
  - `users` table with email, hashed_password
  - Relationship: User has many Todos
- [ ] **Implement JWT authentication**
  - Install `python-jose`, `passlib`, `bcrypt`
  - Create `/auth/register` endpoint
  - Create `/auth/login` endpoint (returns JWT token)
  - Create `/auth/me` endpoint (get current user)
- [ ] **Add authentication dependency**
  - `get_current_user` dependency
  - Protect all Todo endpoints
  - Users can only access their own todos

#### Day 4-5: Database Migrations (3-4 hours)
- [ ] **Setup Alembic** for database migrations
  - Install `alembic`
  - Initialize Alembic
  - Create initial migration
- [ ] **Create migration for Users table**
- [ ] **Add migration for User-Todo relationship**
- [ ] **Learn migration workflow**
  - Create, upgrade, downgrade migrations

#### Day 6-7: Background Tasks & Async (3-4 hours)
- [ ] **Add background task example**
  - Send email notification when todo created (mock)
  - Use FastAPI's `BackgroundTasks`
- [ ] **Convert to async/await** (optional advanced)
  - Use `asyncpg` or `databases` library
  - Convert endpoints to async
  - Learn async database patterns

---

### **Week 5-6: Polish & Deploy** (10-12 hours)

#### Week 5: Performance & Monitoring (5-6 hours)
- [ ] **Add caching** (optional)
  - Install `redis` and `aioredis`
  - Cache frequently accessed todos
  - Cache invalidation on updates
- [ ] **Add performance monitoring**
  - Request timing middleware
  - Slow query logging
- [ ] **Database optimization**
  - Add indexes where needed
  - Use `select_related` to avoid N+1 queries
- [ ] **Add health check endpoint** (`/health`)

#### Week 6: Deployment & Documentation (5-6 hours)
- [ ] **Create `requirements.txt`** with all dependencies
- [ ] **Create `Dockerfile`**
  - Multi-stage build
  - Optimize image size
- [ ] **Create `docker-compose.yml`**
  - API service
  - PostgreSQL database (upgrade from SQLite)
  - Redis (if using caching)
- [ ] **Write comprehensive README.md**
  - Project description
  - Setup instructions
  - API documentation link
  - Testing instructions
- [ ] **Deploy to cloud** (choose one)
  - Render.com (easiest, free tier)
  - Railway.app
  - Heroku
  - AWS/GCP (more advanced)

---

## 📚 Additional Learning Resources

### Recommended Reading Order:
1. **FastAPI Official Docs** - Read "Tutorial - User Guide" sections
2. **SQLAlchemy ORM Tutorial** - Understand relationships and queries
3. **Pydantic Documentation** - Master validation and settings
4. **pytest Documentation** - Learn testing best practices
5. **JWT & OAuth2** - Understand authentication flows

### Practice Projects After Completion:
- **Blog API** - Posts, comments, likes, user profiles
- **E-commerce API** - Products, cart, orders, payments
- **Social Media API** - Posts, followers, feed, notifications

---

## 🎓 Success Metrics

By the end of this roadmap, you should be able to:
- ✅ Build production-ready REST APIs with proper architecture
- ✅ Write comprehensive tests (unit + integration)
- ✅ Implement authentication and authorization
- ✅ Handle errors gracefully with proper logging
- ✅ Deploy APIs to cloud platforms
- ✅ Use database migrations confidently
- ✅ Understand async programming in Python
- ✅ Read and contribute to real-world API codebases

---

## 💡 Tips for Success

1. **Code every day** - Even 30 minutes is better than nothing
2. **Test as you go** - Don't wait until Week 3 to start testing
3. **Read error messages carefully** - They're your best teacher
4. **Use git commits** - Commit after each completed task
5. **Don't skip the basics** - Logging and error handling are crucial
6. **Ask questions** - Use Stack Overflow, Reddit, Discord communities
7. **Build something you care about** - After Week 4, customize the project to your interests

---

## 🚀 Next Immediate Action

**Start here:** Fix the duplicate `get_todo` function in `crud.py` line 46, then add basic logging to all CRUD operations.

Good luck! 🎯
