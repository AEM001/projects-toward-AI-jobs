# FastAPI TODO API 设计文档

## 概述

FastAPI TODO API 是一个 RESTful 风格的任务管理 API，提供完整的 CRUD 操作。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: 1.0.0
- **Content-Type**: `application/json`

## 端点列表

### 1. 创建任务
- **方法**: POST
- **路径**: `/todos`
- **状态码**: 201 Created

### 2. 获取任务列表
- **方法**: GET
- **路径**: `/todos`
- **查询参数**: status, priority, search, sort_by, sort_order, page, page_size

### 3. 获取单个任务
- **方法**: GET
- **路径**: `/todos/{id}`

### 4. 更新任务
- **方法**: PUT
- **路径**: `/todos/{id}`

### 5. 删除任务
- **方法**: DELETE
- **路径**: `/todos/{id}`
- **状态码**: 204 No Content

### 6. 获取统计信息
- **方法**: GET
- **路径**: `/todos/stats`

## 数据模型

### Todo 对象

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | integer | 是 | 任务 ID（自动生成） |
| title | string | 是 | 任务标题（1-200 字符） |
| description | string | 否 | 任务描述（最多 1000 字符） |
| status | enum | 是 | 任务状态（pending, in_progress, done） |
| priority | enum | 是 | 优先级（low, medium, high） |
| created_at | datetime | 是 | 创建时间 |
| updated_at | datetime | 是 | 更新时间 |

## 错误处理

- `400 Bad Request` - 请求格式错误
- `404 Not Found` - 资源不存在
- `422 Unprocessable Entity` - 数据验证失败
- `500 Internal Server Error` - 服务器内部错误
