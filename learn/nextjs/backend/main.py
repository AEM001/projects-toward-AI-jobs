from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Todo API")

# Enable CORS - allows Next.js frontend (port 3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models (same as TypeScript interfaces)
class Todo(BaseModel):
    id: int
    title: str
    completed: bool
    createdAt: str

class CreateTodoRequest(BaseModel):
    title: str

class UpdateTodoRequest(BaseModel):
    completed: bool

# In-memory storage
_todos: List[Todo] = [
    Todo(id=1, title="Learn FastAPI", completed=False, createdAt=datetime.now().isoformat()),
    Todo(id=2, title="Build a todo app", completed=True, createdAt=datetime.now().isoformat()),
]
_next_id = 3

@app.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos"""
    return _todos

@app.post("/todos", response_model=Todo)
async def create_todo(request: CreateTodoRequest):
    """Create a new todo"""
    global _next_id
    new_todo = Todo(
        id=_next_id,
        title=request.title,
        completed=False,
        createdAt=datetime.now().isoformat()
    )
    _next_id += 1
    _todos.append(new_todo)
    return new_todo

@app.get("/")
async def root():
    return {"message": "Todo API is running", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
