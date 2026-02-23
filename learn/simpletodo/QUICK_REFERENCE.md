# 📋 快速参考卡片

## 🚀 一键启动

```bash
cd /Users/Mac/code/project/fun
./start.sh
```

访问：**http://localhost:5173**

---

## 🛑 一键停止

```bash
cd /Users/Mac/code/project/fun
./stop.sh
```

---

## 🌐 端口地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

---

## 📁 项目结构

```
/Users/Mac/code/project/fun/
├── start.sh          # 启动脚本
├── stop.sh           # 停止脚本
├── README.md         # 项目文档
├── QUICKSTART.md     # 快速启动指南
├── USAGE.md          # 使用说明
├── PROJECT_SUMMARY.md # 项目总结
│
├── backend/          # 后端 (FastAPI)
│   ├── main.py      # 主程序
│   ├── models.py    # 数据模型
│   ├── auth.py      # 认证
│   └── ...
│
└── frontend/         # 前端 (Vue 3)
    ├── src/
    │   ├── api.js   # API 封装
    │   └── components/
    │       ├── Login.vue
    │       └── TaskList.vue
    └── ...
```

---

## 🔧 常用命令

### 启动服务
```bash
./start.sh
```

### 停止服务
```bash
./stop.sh
```

### 查看日志
```bash
# 后端日志
tail -f /tmp/backend.log

# 前端日志
tail -f /tmp/frontend.log
```

### 测试 API
```bash
# 测试根路径
curl http://localhost:8000/

# 查看 API 文档
open http://localhost:8000/docs
```

### 重置数据
```bash
cd backend
rm tasks.db
./stop.sh
./start.sh
```

---

## 📝 API 接口速查

### 认证
```
POST /auth/register
  body: {"email": "...", "password": "..."}

POST /auth/login
  body: {"email": "...", "password": "..."}
  返回: {"access_token": "...", "token_type": "bearer"}
```

### 任务
```
GET /tasks
  headers: Authorization: Bearer <token>
  返回: 任务列表

POST /tasks
  headers: Authorization: Bearer <token>
  body: {"title": "...", "description": "..."}
  返回: 创建的任务

PUT /tasks/{id}
  headers: Authorization: Bearer <token>
  body: {"status": "pending/in_progress/completed"}
  返回: 更新后的任务

DELETE /tasks/{id}
  headers: Authorization: Bearer <token>
  返回: {"message": "Task deleted successfully"}
```

---

## 🎨 状态颜色

| 状态 | 颜色 | 标识 |
|------|------|------|
| 待办 | 🟣 紫色 | pending |
| 进行中 | 🟠 橙色 | in_progress |
| 已完成 | 🟢 绿色 | completed |

---

## 📖 文档索引

| 文件 | 说明 |
|------|------|
| README.md | 项目介绍和功能 |
| QUICKSTART.md | 快速启动指南 |
| USAGE.md | 详细使用说明 |
| PROJECT_SUMMARY.md | 项目完成总结 |
| QUICK_REFERENCE.md | 本文件（快速参考） |

---

## 🎯 使用流程

### 1. 启动
```bash
./start.sh
```

### 2. 访问
打开浏览器 → http://localhost:5173

### 3. 注册/登录
输入邮箱和密码

### 4. 创建任务
输入标题 → 点击添加

### 5. 管理任务
- 切换状态：下拉菜单选择
- 删除任务：点击删除按钮

### 6. 退出
点击右上角"退出登录"

---

## 🔍 故障排查

### 问题：端口被占用

**解决：**
```bash
# 修改后端端口 (backend/main.py)
uvicorn.run(app, host="0.0.0.0", port=8001)

# 修改前端配置 (frontend/vite.config.js)
server: { port: 5174 }

# 修改 API 地址 (frontend/.env)
VITE_API_URL=http://localhost:8001
```

### 问题：依赖安装失败

**解决：**
```bash
# 后端
cd backend
pip install --upgrade -r requirements.txt

# 前端
cd frontend
rm -rf node_modules
npm install
```

### 问题：数据库错误

**解决：**
```bash
cd backend
rm tasks.db
./stop.sh
./start.sh
```

---

## 📊 项目信息

- **开始时间**：2026-01-16
- **代码行数**：~1060 行
- **文件数量**：~25 个
- **难度等级**：⭐⭐ 入门级
- **开发时长**：约 2 小时

---

## 🎓 学习要点

### 后端
- FastAPI 路由系统
- JWT 认证机制
- SQLModel ORM
- Pydantic 数据验证

### 前端
- Vue 3 Composition API
- Vue Router 路由
- API 封装和调用
- 组件化开发

### 前后端联调
- RESTful API 设计
- CORS 配置
- Token 认证流程

---

## 🚀 扩展建议

### 功能增强
- 任务筛选
- 任务搜索
- 任务截止日期
- 任务优先级

### UI 优化
- 深色模式
- 动画效果
- 响应式优化
- 数据图表

### 后端优化
- 数据库迁移
- 单元测试
- Docker 部署
- 性能优化

---

## 📞 获取帮助

1. **查看日志**
   ```bash
   tail -f /tmp/backend.log
   tail -f /tmp/frontend.log
   ```

2. **查看 API 文档**
   ```
   http://localhost:8000/docs
   ```

3. **重启服务**
   ```bash
   ./stop.sh
   ./start.sh
   ```

---

## 🎉 总结

**启动项目：**
```bash
./start.sh
```

**访问地址：**
```
http://localhost:5173
```

**停止项目：**
```bash
./stop.sh
```

**就这么简单！** 🚀

---

**祝你使用愉快！** 🎉
