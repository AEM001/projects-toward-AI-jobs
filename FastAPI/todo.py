from fastapi import FastAPI
from pydantic import BaseModel, Field,Config
from fastapi import HTTPException
from db import TodoDB,SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session

app=FastAPI(title="Simple Todo API")
todos=[]
next_id=1

class TodoCreate(BaseModel):
    title:str=Field(min_length=1,description="Todo title, cannot be empty")

class Todo(BaseModel):
    id:int
    title:str
    done:bool

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/todos",response_model=Todo,status_code=201)
def create_todo(todo:TodoCreate):
    global next_id
    new_todo={
        "id":next_id,
        "title":todo.title,
        "done":False
    }
    next_id+=1
    todos.append(new_todo)
    return new_todo

@app.get("/todos",response_model=list[Todo])
def list_todos():
    return todos

@app.get("/todos/{id}",response_model=Todo)
def get_todo(id:int):
    for i in todos:
        if i["id"]==id:
            return i

    raise HTTPException(status_code=404,detail="Todo not found")

class TodoUpdate(BaseModel):
    title:str| None=Field(default=None, description="更新任务标题，留空则不修改", json_schema_extra={"example": None})
    done:bool| None=Field(default=None, description="更新任务状态，留空则不修改", json_schema_extra={"example": None})

@app.patch("/todos/{id}",response_model=Todo)
def update_todo(id:int,update:TodoUpdate):
    for i in todos:
        if i["id"]==id:
            if update.title is not None:
                i["title"]=update.title
            if update.done is not None:
                i["done"]=update.done
            return i

    raise HTTPException(status_code=404,detail="Todo not found")

@app.delete("/todos/{id}",status_code=204)
def delete_todo(id:int):
    for index,t in enumerate(todos):
        if t["id"]==id:
            todos.pop(index)
            return
    raise HTTPException(status_code=404,detail="Todo not found")