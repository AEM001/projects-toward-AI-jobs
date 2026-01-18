from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from fastapi import HTTPException
from db import TodoDB,SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session

app=FastAPI(title="Simple Todo API")
# Depends + yield = 请求级生命周期管理（创建→使用→清理）
# 每次请求都会调用get_db函数, 创建一个SessionLocal实例，管理数据库连接，包含注入路由参数
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ——————————————Pydantic Models——————————————

class TodoCreate(BaseModel):
    title:str=Field(min_length=1,description="Todo title, cannot be empty")

class Todo(BaseModel):
    model_config=ConfigDict(from_attributes=True)#允许从ORM对象读取属性
    
    id:int
    title:str
    done:bool

class TodoUpdate(BaseModel):
    title:str| None=Field(default=None, description="更新任务标题，留空则不修改", json_schema_extra={"example": None})
    done:bool| None=Field(default=None, description="更新任务状态，留空则不修改", json_schema_extra={"example": None})

# ——————————————FastAPI Routes——————————————

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/todos",response_model=Todo,status_code=201)
def create_todo(todo:TodoCreate,db:Session=Depends(get_db)):
    db_todo=TodoDB(title=todo.title,done=False)
    # 一句话：add=登记；commit=真正写入+提交事务；refresh=把数据库生成的字段拉回对象。
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
# 对于 每一次 HTTP 请求，FastAPI 会：
# 调用 get_db()
# 创建一个新的 Session
# 把这个 Session 注入到参数 db
# 路由函数执行完后自动关闭 Session

@app.get("/todos",response_model=list[Todo])
def list_todos(db:Session=Depends(get_db)):
    return db.query(TodoDB).order_by(TodoDB.id.asc()).all()

@app.get("/todos/{id}",response_model=Todo)
def get_todo(id:int,db:Session=Depends(get_db)):
    db_todo=db.query(TodoDB).filter(TodoDB.id==id).first()
    if db_todo is None:
        raise HTTPException(status=404,detail="todo not found")
    return db_todo#pydantic会自动将ORM对象转换



def update_todo(id: int, update: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if update.title is not None:
        db_todo.title = update.title
    if update.done is not None:
        db_todo.done = update.done

    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoDB).filter(TodoDB.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()
    return