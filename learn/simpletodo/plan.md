# 任务管理系统 - 项目规划文档

## 📋 项目概述

这是一个轻量级的前后端闭环任务管理系统，用于快速体验全栈开发。功能简单，代码精简，适合学习和演示。

## 🎯 核心功能（精简版）

### 1. 用户管理
- 用户注册/登录（JWT 认证）

### 2. 任务管理
- 创建任务（标题、描述）
- 查看任务列表
- 更新任务状态（待办 → 进行中 → 已完成）
- 删除任务

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: SQLite（单文件，无需安装）
- **ORM**: SQLModel (FastAPI 官方推荐)
- **认证**: JWT (PyJWT)
- **API 文档**: 自动 Swagger UI

### 前端
- **框架**: Vue 3 + Composition API（简单易学）
- **构建工具**: Vite（快速开发服务器）
- **状态管理**: Vue 3 响应式 API（内置）
- **UI 库**: 原生 CSS + 简单组件
- **HTTP 客户端**: Fetch API（原生）

### 开发工具
- **Python**: 3.8+
- **包管理**: pip / poetry
- **热重载**: 自动重启

## 📁 项目结构

```
task-manager/
├── README.md
├── plan.md
├── .gitignore
│
├── backend/                  # 后端 (FastAPI)
│   ├── requirements.txt      # 依赖列表
│   ├── main.py              # 主程序
│   ├── database.py          # 数据库配置
│   ├── models.py            # 数据模型
│   ├── schemas.py           # Pydantic 模型
│   ├── crud.py              # 数据操作
│   ├── auth.py              # 认证逻辑
│   └── tasks.db             # SQLite 数据库（自动生成）
│
└── frontend/                # 前端 (Vue 3 + Vite)
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── src/
    │   ├── main.js          # 入口
    │   ├── App.vue          # 根组件
    │   ├── api.js           # API 调用
    │   ├── components/      # 组件
    │   │   ├── Login.vue
    │   │   ├── TaskList.vue
    │   │   └── TaskForm.vue
    │   └── style.css        # 样式
    └── public/
```

## 🗄️ 数据库设计

### User 模型
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
```

### Task 模型
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in_progress, completed
    created_at: datetime = Field(default_factory=datetime.now)

    user_id: int = Field(foreign_key="user.id")
```

### 状态流转
```
pending → in_progress → completed
```

## 🔌 API 设计

### 认证相关
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 返回 JWT token

### 任务相关
- `GET /tasks` - 获取当前用户的任务列表
- `POST /tasks` - 创建任务
- `PUT /tasks/{task_id}` - 更新任务（状态）
- `DELETE /tasks/{task_id}` - 删除任务

### 测试 API
- `GET /` - 欢迎信息
- `GET /docs` - Swagger UI 文档

## 📦 依赖版本

### 后端依赖 (requirements.txt)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### 前端依赖 (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

## 🚀 开发流程

### 1. 初始化项目
```bash
# 创建项目目录
mkdir task-manager && cd task-manager

# 初始化后端
mkdir backend && cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn sqlmodel python-jose passlib python-multipart
# 创建文件...

# 初始化前端
cd ..
npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

### 2. 开发步骤
1. **后端开发** (backend/)
   - 配置 FastAPI 服务器
   - 设置 SQLite 数据库
   - 实现用户认证 (JWT)
   - 实现任务 CRUD API
   - 添加数据验证

2. **前端开发** (frontend/)
   - 配置 Vue 3 项目
   - 实现登录/注册页面
   - 实现任务列表展示
   - 实现任务创建表单
   - 实现任务状态切换

3. **集成测试**
   - 测试 API (Swagger UI)
   - 测试前端功能

## 📝 开发里程碑

### Phase 1: 后端 API（1-2 小时）
- ✅ FastAPI 项目初始化
- ✅ SQLite 数据库配置
- ✅ 用户注册/登录 API
- ✅ 任务 CRUD API
- ✅ Swagger UI 文档

### Phase 2: 前端界面（2-3 小时）
- ✅ Vue 3 + Vite 初始化
- ✅ 登录/注册页面
- ✅ 任务列表页面
- ✅ 任务创建表单
- ✅ 状态切换功能

### Phase 3: 集成测试（30 分钟）
- ✅ API 测试
- ✅ 前端联调
- ✅ 完整流程测试

## 🔧 环境变量

### 后端 (.env)
```env
DATABASE_URL=sqlite:///./tasks.db
JWT_SECRET=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端 (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 📚 学习收获

通过这个项目，你将掌握：
- ✅ FastAPI 快速开发 RESTful API
- ✅ SQLModel 操作 SQLite 数据库
- ✅ JWT 认证和授权机制
- ✅ Vue 3 Composition API 开发
- ✅ 前端状态管理（响应式 API）
- ✅ 原生 CSS 样式开发
- ✅ 前后端联调和 CORS 配置
- ✅ Swagger UI API 文档使用

## 🎓 扩展功能（可选）

完成基础功能后，可以考虑添加：
- 任务筛选和搜索
- 任务分类/标签
- 任务截止日期提醒
- 数据统计图表
- 深色模式支持
- 响应式移动端适配

---

**开始时间**: 2026-01-16
**预计完成**: 1 天内（3-5 小时）
**难度等级**: ⭐⭐ 入门级
