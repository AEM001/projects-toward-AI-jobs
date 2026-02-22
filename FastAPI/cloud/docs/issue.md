# Issues & Problems Record

## 2026-02-15: Swagger UI Loading Failed Due to Content Security Policy

### Problem
When accessing `/docs` (Swagger UI), the page couldn't load external resources (CSS, JS, favicon) because of a strict Content Security Policy.

### Error Messages
```
Loading the stylesheet 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css' violates Content-Security-Policy directive: "default-src 'self'"
Loading the script 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js' violates Content-Security-Policy directive: "default-src 'self'"
Loading the image 'https://fastapi.tiangolo.com/img/favicon.png' violates Content-Security-Policy directive: "default-src 'self'"
Executing inline script violates Content-Security-Policy directive 'default-src 'self''
```

### Root Cause
In `main.py` line 156, a middleware was adding a strict CSP header:
```python
response.headers["Content-Security-Policy"] = "default-src 'self'"
```

This blocks all external resources (CDN, favicon) and inline scripts.

### Solution
Updated CSP to allow necessary external domains:
```python
response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net https://fastapi.tiangolo.com 'unsafe-inline'"
```

### Files Modified
- `main.py` - Updated CSP middleware

### Lessons Learned
1. When using Swagger UI or other frontend tools, need to configure CSP to allow external CDN resources
2. `'unsafe-inline'` is needed for inline scripts that Swagger UI generates
3. Consider disabling CSP in development mode, or create separate CSP configs for dev/prod
