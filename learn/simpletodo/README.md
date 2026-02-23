# 任务管理系统 - Tiny Project

一个轻量级的前后端闭环任务管理系统，用于快速体验全栈开发。

## 🎯 功能特性

- ✅ 用户注册/登录（JWT 认证）
- ✅ 创建任务（标题、描述）
- ✅ 查看任务列表
- ✅ 更新任务状态（待办 → 进行中 → 已完成）
- ✅ 删除任务
- ✅ Swagger UI API 文档

## 🛠️ 技术栈

### 后端
- **FastAPI** - Python Web 框架
- **SQLModel** - ORM（SQLite 数据库）
- **PyJWT** - JWT 认证
- **Uvicorn** - ASGI 服务器

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 构建工具
- **Vue Router** - 路由管理
- **Fetch API** - HTTP 客户端

## 📁 项目结构


```
task-manager/
├── backend/              # 后端 (FastAPI)
│   ├── main.py          # 主程序
│   ├── database.py      # 数据库配置
│   ├── models.py        # 数据模型
│   ├── schemas.py       # Pydantic 模型
│   ├── auth.py          # 认证逻辑
│   ├── crud.py          # 数据操作
│   ├── requirements.txt # 依赖
│   └── .env             # 环境变量
│
└── frontend/            # 前端 (Vue 3)
    ├── src/
    │   ├── main.js      # 入口
    │   ├── App.vue      # 根组件
    │   ├── router.js    # 路由
    │   ├── api.js       # API 封装
    │   └── components/
    │       ├── Login.vue
    │       └── TaskList.vue
    └── package.json
```

## 🚀 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --reload --port 8000
```

后端服务将在 http://localhost:8000 启动

**API 文档**: http://localhost:8000/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 3. 使用流程

1. **注册/登录**
   - 访问 http://localhost:5173
   - 输入邮箱和密码注册或登录

2. **管理任务**
   - 在输入框中添加新任务
   - 点击下拉菜单切换任务状态
   - 点击删除按钮删除任务

3. **查看 API 文档**
   - 访问 http://localhost:8000/docs
   - 可以直接测试所有 API 接口

## 🔌 API 接口

### 认证
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录

### 任务
- `GET /tasks` - 获取任务列表
- `POST /tasks` - 创建任务
- `PUT /tasks/{id}` - 更新任务
- `DELETE /tasks/{id}` - 删除任务

## 📝 数据库模型

### User
- `id` - 用户 ID
- `email` - 邮箱（唯一）
- `hashed_password` - 密码哈希
- `created_at` - 创建时间

### Task
- `id` - 任务 ID
- `title` - 标题
- `description` - 描述（可选）
- `status` - 状态（pending/in_progress/completed）
- `created_at` - 创建时间
- `user_id` - 用户 ID（外键）

## 🎓 学习要点

通过这个项目，你可以学习到：

1. **FastAPI 基础**
   - 路由定义
   - 依赖注入
   - Pydantic 数据验证
   - JWT 认证

2. **SQLModel 使用**
   - 模型定义
   - 数据库操作
   - 关系映射

3. **Vue 3 核心**
   - Composition API
   - 组件开发
   - 响应式数据

4. **前端路由**
   - Vue Router 配置
   - 路由守卫
   - 权限控制

5. **前后端联调**
   - RESTful API 设计
   - CORS 配置
   - Token 认证

## 🔧 环境变量

### backend/.env
```env
DATABASE_URL=sqlite:///./tasks.db
JWT_SECRET=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### frontend/.env
```env
VITE_API_URL=http://localhost:8000
```

## 📦 依赖版本

### 后端 (requirements.txt)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

### 前端 (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

## 🎨 界面预览

### 登录/注册页面
- 渐变背景
- 卡片式表单
- 模式切换（登录/注册）
- 错误/成功提示

### 任务列表页面
- 任务创建表单
- 任务卡片列表
- 状态标签（彩色）
- 状态切换下拉菜单
- 删除按钮
- 退出登录

## 🚀 扩展建议

完成基础功能后，可以尝试：

1. **功能增强**
   - 任务筛选和搜索
   - 任务截止日期
   - 任务分类/标签
   - 任务优先级

2. **UI 优化**
   - 深色模式
   - 动画效果
   - 任务拖拽排序
   - 数据统计图表

3. **后端优化**
   - 数据库迁移（Alembic）
   - 邮件通知
   - 文件上传
   - 缓存优化

4. **部署**
   - Docker 容器化
   - 云服务器部署
   - CI/CD 流程

---

**开始时间**: 2026-01-16
**预计时长**: 3-5 小时
**难度**: ⭐⭐ 入门级
