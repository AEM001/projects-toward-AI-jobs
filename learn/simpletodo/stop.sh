#!/bin/bash

# 停止任务管理系统服务

echo "========================================="
echo "  停止任务管理系统"
echo "========================================="
echo ""

# 停止后端
if [ -f "/tmp/task_manager_backend.pid" ]; then
    PID=$(cat /tmp/task_manager_backend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "正在停止后端服务 (PID: $PID)..."
        kill $PID
        echo "✅ 后端已停止"
    else
        echo "后端服务未运行"
    fi
    rm /tmp/task_manager_backend.pid
else
    echo "后端 PID 文件不存在，尝试查找进程..."
    pkill -f "uvicorn main:app" && echo "✅ 后端已停止" || echo "后端未运行"
fi

# 停止前端
if [ -f "/tmp/task_manager_frontend.pid" ]; then
    PID=$(cat /tmp/task_manager_frontend.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "正在停止前端服务 (PID: $PID)..."
        kill $PID
        echo "✅ 前端已停止"
    else
        echo "前端服务未运行"
    fi
    rm /tmp/task_manager_frontend.pid
else
    echo "前端 PID 文件不存在，尝试查找进程..."
    pkill -f "vite" && echo "✅ 前端已停止" || echo "前端未运行"
fi

echo ""
echo "========================================="
echo "  所有服务已停止"
echo "========================================="
