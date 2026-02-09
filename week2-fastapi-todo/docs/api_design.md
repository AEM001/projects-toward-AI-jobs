# FastAPI TODO API Design Documentation

## Overview

FastAPI TODO API is a RESTful-style task management API that provides complete CRUD operations.

## Basic Information

- **Base URL**: `http://localhost:8000`
- **API Version**: 1.0.0
- **Content-Type**: `application/json`

## Endpoint List

### 1. Create Task
- **Method**: POST
- **Path**: `/todos`
- **Status Code**: 201 Created

### 2. Get Task List
- **Method**: GET
- **Path**: `/todos`
- **Query Parameters**: status, priority, search, sort_by, sort_order, page, page_size

### 3. Get Single Task
- **Method**: GET
- **Path**: `/todos/{id}`

### 4. Update Task
- **Method**: PUT
- **Path**: `/todos/{id}`

### 5. Delete Task
- **Method**: DELETE
- **Path**: `/todos/{id}`
- **Status Code**: 204 No Content

### 6. Get Statistics
- **Method**: GET
- **Path**: `/todos/stats`

## Data Models

### Todo Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Task ID (auto-generated) |
| title | string | Yes | Task title (1-200 characters) |
| description | string | No | Task description (max 1000 characters) |
| status | enum | Yes | Task status (pending, in_progress, done) |
| priority | enum | Yes | Priority (low, medium, high) |
| created_at | datetime | Yes | Creation time |
| updated_at | datetime | Yes | Update time |

## Error Handling

- `400 Bad Request` - Request format error
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Data validation failed
- `500 Internal Server Error` - Server internal error
