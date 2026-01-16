#!/bin/bash

# 任务管理系统 - 快速启动脚本

echo "========================================="
echo "  任务管理系统 - 快速启动"
echo "========================================="
echo ""

# 检查是否在正确的目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   cd /Users/Mac/code/project/fun"
    exit 1
fi

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 1. 启动后端
echo "步骤 1: 启动后端服务 (FastAPI)"
echo "-------------------------------------"

cd backend

# 检查是否已安装依赖
if [ ! -d "venv" ] && ! python -c "import fastapi" 2>/dev/null; then
    echo "正在安装后端依赖..."
    pip install -r requirements.txt
fi

# 启动后端
echo "启动后端服务: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""

# 在后台启动并记录 PID
uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/task_manager_backend.pid

cd ..

# 等待后端启动
sleep 2

# 检查后端是否启动成功
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ 后端启动成功！"
else
    echo "❌ 后端启动失败，请查看 /tmp/backend.log"
    exit 1
fi

echo ""

# 2. 启动前端
echo "步骤 2: 启动前端服务 (Vue 3)"
echo "-------------------------------------"

cd frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
fi

# 启动前端
echo "启动前端服务: http://localhost:5173"
echo ""

# 在后台启动并记录 PID
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/task_manager_frontend.pid

cd ..

# 等待前端启动
sleep 3

# 检查前端是否启动成功
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端启动成功！"
else
    echo "❌ 前端启动失败，请查看 /tmp/frontend.log"
    exit 1
fi

echo ""
echo "========================================="
echo "  🎉 项目启动成功！"
echo "========================================="
echo ""
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "使用方法:"
echo "  1. 访问 http://localhost:5173"
echo "  2. 输入邮箱和密码注册/登录"
echo "  3. 创建和管理任务"
echo ""
echo "停止服务:"
echo "  ./stop.sh"
echo ""
echo "查看日志:"
echo "  后端: tail -f /tmp/backend.log"
echo "  前端: tail -f /tmp/frontend.log"
echo ""
