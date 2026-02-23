# 快速启动指南

## 🚀 最简单的方式（推荐）

### 1. 启动项目

在项目根目录运行：

```bash
./start.sh
```

脚本会自动：
- ✅ 检查环境（Python、Node.js）
- ✅ 安装依赖（如果需要）
- ✅ 启动后端服务（端口 8000）
- ✅ 启动前端服务（端口 5173）

### 2. 使用浏览器访问

启动成功后，在浏览器中打开：

**http://localhost:5173**

### 3. 停止项目

```bash
./stop.sh
```

---

## 📝 详细使用步骤

### 第一次使用

#### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd ../frontend
npm install
```

#### 2. 启动服务

**方式一：使用脚本（推荐）**
```bash
cd /Users/Mac/code/project/fun
./start.sh
```

**方式二：手动启动**

终端 1 - 后端：
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

终端 2 - 前端：
```bash
cd frontend
npm run dev
```

#### 3. 访问应用

在浏览器中打开：**http://localhost:5173**

---

## 🎯 使用流程

### 1. 注册/登录

```
打开浏览器 → http://localhost:5173
├── 输入邮箱（如: test@example.com）
├── 输入密码
├── 点击"注册"或"登录"
└── 自动跳转到任务列表
```

### 2. 创建任务

```
任务列表页面
├── 在"任务标题"输入框输入标题
├── 在"任务描述"输入框输入描述（可选）
├── 点击"添加任务"按钮
└── 任务出现在列表顶部
```

### 3. 管理任务

```
每个任务卡片包含：
├── 状态标签（待办/进行中/已完成）
├── 状态下拉菜单 → 切换状态
├── 删除按钮 → 删除任务
└── 创建时间
```

### 4. 查看 API 文档

访问：**http://localhost:8000/docs**

可以直接测试所有 API 接口！

---

## 🔍 常见问题

### Q: 端口被占用怎么办？

**后端端口 (8000) 被占用：**
```bash
# 修改 backend/main.py 最后一行
uvicorn.run(app, host="0.0.0.0", port=8001)  # 改为 8001

# 同时修改 frontend/.env
VITE_API_URL=http://localhost:8001
```

**前端端口 (5173) 被占用：**
```bash
# 修改 frontend/vite.config.js
server: {
  port: 5174,  # 改为 5174
}
```

### Q: 如何查看日志？

```bash
# 后端日志
tail -f /tmp/backend.log

# 前端日志
tail -f /tmp/frontend.log
```

### Q: 如何重置数据？

```bash
# 删除数据库文件
cd backend
rm tasks.db

# 重启服务
./stop.sh
./start.sh
```

### Q: 导入依赖失败？

```bash
# 后端
cd backend
pip install --upgrade -r requirements.txt

# 前端
cd frontend
rm -rf node_modules
npm install
```

---

## 📊 项目信息

### 端口说明
- **前端**: http://localhost:5173
- **后端**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 文件说明
```
project/
├── start.sh          # 一键启动脚本
├── stop.sh           # 一键停止脚本
├── README.md         # 项目文档
├── QUICKSTART.md     # 快速启动指南（本文件）
├── plan.md           # 项目规划
├── backend/          # 后端代码
└── frontend/         # 前端代码
```

### 数据存储
- **数据库**: `backend/tasks.db` (SQLite)
- **Token**: 浏览器 localStorage

---

## 🎓 学习建议

1. **先运行起来**
   - 使用 `./start.sh` 快速启动
   - 体验完整功能

2. **查看代码**
   - 阅读 `backend/main.py` 了解 API
   - 阅读 `frontend/src/api.js` 了解前端调用

3. **尝试修改**
   - 修改前端样式
   - 添加新功能
   - 修改 API

4. **查看 API 文档**
   - 访问 http://localhost:8000/docs
   - 了解每个接口的用法

---

## 🚀 下一步

完成基础体验后，可以尝试：

1. **添加功能**
   - 任务筛选
   - 任务搜索
   - 任务截止日期

2. **优化 UI**
   - 添加动画效果
   - 深色模式
   - 响应式优化

3. **学习进阶**
   - 数据库迁移（Alembic）
   - 单元测试
   - Docker 部署

---

**祝你学习愉快！** 🎉
