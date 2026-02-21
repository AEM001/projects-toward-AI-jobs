# FastAPI Testing Commands

## Quick Start

```bash
# Start server (in one terminal)
cd /Users/Mac/code/project/FastAPI
uvicorn main:app --reload

# Watch logs (in another terminal)
tail -f /Users/Mac/code/project/FastAPI/app.log
```

---

## Authentication Commands

### Register User
```bash
curl -X POST 'http://127.0.0.1:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{"email": "testuser@example.com", "password": "testpass123"}'
```

### Login (Get Token)
```bash
# Store token in variable
TOKEN=$(curl -s -X POST 'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email": "testuser@example.com", "password": "testpass123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Or just see the response
curl -X POST 'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email": "testuser@example.com", "password": "testpass123"}'
```

---

## Todo Operations

### Create Todo
```bash
curl -X POST 'http://127.0.0.1:8000/todos' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Test todo", "ddl": "2024-12-31 23:59"}'
```

### List All Todos
```bash
curl -X GET 'http://127.0.0.1:8000/todos?skip=0&limit=50' \
  -H "Authorization: Bearer $TOKEN"
```

### Get Specific Todo
```bash
curl -X GET 'http://127.0.0.1:8000/todos/1' \
  -H "Authorization: Bearer $TOKEN"
```

### Update Todo
```bash
curl -X PUT 'http://127.0.0.1:8000/todos/1' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Updated title", "completed": true}'
```

### Delete Todo
```bash
curl -X DELETE 'http://127.0.0.1:8000/todos/1' \
  -H "Authorization: Bearer $TOKEN"
```

---

## Filter & Search

### Filter by Week
```bash
curl -X GET 'http://127.0.0.1:8000/todos?filter_week=true' \
  -H "Authorization: Bearer $TOKEN"
```

### Filter by Status
```bash
curl -X GET 'http://127.0.0.1:8000/todos?completed=true' \
  -H "Authorization: Bearer $TOKEN"
```

### Sort Options
```bash
# Sort by deadline (newest first)
curl -X GET 'http://127.0.0.1:8000/todos?sort_by=ddl&sort_order=desc' \
  -H "Authorization: Bearer $TOKEN"

# Sort by created date (oldest first)
curl -X GET 'http://127.0.0.1:8000/todos?sort_by=created_at&sort_order=asc' \
  -H "Authorization: Bearer $TOKEN"
```

---

## Health & Debug

### Health Check
```bash
curl -X GET 'http://127.0.0.1:8000/health'
```

### Debug Info
```bash
curl -X GET 'http://127.0.0.1:8000/debug/info' \
  -H "Authorization: Bearer $TOKEN"
```

---

## Rate Limiting Test

### Test Rate Limit (20 requests/minute)
```bash
# This will hit the rate limit after 20 requests
for i in {1..25}; do
  echo "Request $i:"
  curl -s -X GET 'http://127.0.0.1:8000/todos' \
    -H "Authorization: Bearer $TOKEN" | jq '.total'
  sleep 0.1
done
```

---

## Pretty Print JSON

### Add `| jq` for formatted output
```bash
curl -X GET 'http://127.0.0.1:8000/todos?limit=5' \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Extract specific fields
```bash
# Just get todo titles
curl -X GET 'http://127.0.0.1:8000/todos?limit=5' \
  -H "Authorization: Bearer $TOKEN" | jq '.items[].title'

# Get total count
curl -X GET 'http://127.0.0.1:8000/todos' \
  -H "Authorization: Bearer $TOKEN" | jq '.total'
```

---

## One-Liner Scripts

### Create Multiple Todos
```bash
# Create 5 todos quickly
for i in {1..5}; do
  curl -X POST 'http://127.0.0.1:8000/todos' \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"title\": \"Todo $i\", \"ddl\": \"2024-12-$((30-i%10)) 23:59\"}"
  sleep 0.5
done
```

### Test All Endpoints
```bash
# Complete workflow test
echo "=== Health ==="
curl -s 'http://127.0.0.1:8000/health'

echo -e "\n=== Login ==="
TOKEN=$(curl -s -X POST 'http://127.0.0.1:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email": "testuser@example.com", "password": "testpass123"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo -e "\n=== Create Todo ==="
curl -s -X POST 'http://127.0.0.1:8000/todos' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "Test from script", "ddl": "2024-12-31 23:59"}' | jq '.'

echo -e "\n=== List Todos ==="
curl -s -X GET 'http://127.0.0.1:8000/todos?limit=3' \
  -H "Authorization: Bearer $TOKEN" | jq '.items[].title'
```

---

## Tips

1. **Always check logs** after running commands:
   ```bash
   tail -5 /Users/Mac/code/project/FastAPI/app.log
   ```

2. **Use `-s` flag** to silence progress meters in scripts

3. **Check response headers** for timing info:
   ```bash
   curl -I 'http://127.0.0.1:8000/health'
   # Look for: X-Request-Duration: 0.0059s
   ```

4. **Test errors** with invalid data:
   ```bash
   # Invalid token
   curl -X GET 'http://127.0.0.1:8000/todos' \
     -H "Authorization: Bearer invalid_token"

   # Missing required fields
   curl -X POST 'http://127.0.0.1:8000/todos' \
     -H 'Content-Type: application/json' \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"title": ""}'
   ```
