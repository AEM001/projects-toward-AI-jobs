# ========================================
# 📦 导入模块和初始化
# ========================================
from fastapi import FastAPI
from pydantic import BaseModel, Field, ConfigDict
from fastapi import HTTPException
from db import TodoDB,SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session
import time

app=FastAPI(title="Simple Todo API")

# ========================================
# 🗄️ 数据库依赖注入 - 实验核心
# ========================================
# 实验1: 请求级事务管理
# - 自动提交: yield 后执行 db.commit()
# - 自动回滚: 异常时执行 db.rollback()
# - 自动关闭: finally 中执行 db.close()
def get_db_tx():
    db:Session=SessionLocal()
    print(f"[get_db_tx] OEPN db_id={id(db)}")
    try:
        yield db
        db.commit()  # ✅ 自动提交事务
    except Exception as e:
        db.rollback()  # ✅ 自动回滚事务
        print(f"[get_db_tx] ROLLBACK db_id={id(db)} err={e!r}")
        raise
    finally:
        db.close()  # ✅ 自动关闭连接
        print(f"[get_db_tx] CLOSED db_id={id(db)}")

# ========================================
# 📋 Pydantic 数据模型
# ========================================

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

# ========================================
# 🚀 Todo CRUD API 路由
# ========================================

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/todos",response_model=Todo,status_code=201)
def create_todo(todo:TodoCreate,db:Session=Depends(get_db_tx)):
    """创建Todo - 使用自动事务管理"""
    db_todo=TodoDB(title=todo.title,done=False)
    db.add(db_todo)
    # 注意: get_db_tx 会自动提交，无需手动 db.commit()
    db.refresh(db_todo)  # ✅ 必须保留 - 获取数据库生成的ID
    return db_todo

@app.get("/todos",response_model=list[Todo])
def list_todos(db:Session=Depends(get_db)):
    """获取所有Todo - 使用传统方式(对比实验)"""
    return db.query(TodoDB).order_by(TodoDB.id.asc()).all()

@app.get("/todos/{id}",response_model=Todo)
def get_todo(id:int,db:Session=Depends(get_db)):
    """获取单个Todo - 使用传统方式"""
    db_todo=db.query(TodoDB).filter(TodoDB.id==id).first()
    if db_todo is None:
        raise HTTPException(status_code=404,detail="todo not found")
    return db_todo  # Pydantic自动将ORM对象转换

@app.put("/todos/{id}", response_model=Todo)
def update_todo(id: int, update: TodoUpdate, db: Session = Depends(get_db)):
    """更新Todo - 使用传统方式(需要手动commit)"""
    db_todo = db.query(TodoDB).filter(TodoDB.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if update.title is not None:
        db_todo.title = update.title
    if update.done is not None:
        db_todo.done = update.done

    # 注意: 使用get_db时需要手动提交，使用get_db_tx时则不需要
    # db.commit()  # 手动提交(传统方式)
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int, db: Session = Depends(get_db)):
    """删除Todo - 使用传统方式(需要手动commit)"""
    db_todo = db.query(TodoDB).filter(TodoDB.id == id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    # db.commit()  # 手动提交(传统方式)
    return

# ========================================
# 🐛 调试和实验路由
# ========================================

# 基础数据库连接测试
@app.get("/debug/db-ok")
def db_ok(db:Session=Depends(get_db)):
    """测试数据库连接正常"""
    return {"msg":"db ok"}

@app.get("/debug/db_error")
def db_error(db:Session=Depends(get_db)):
    """测试异常处理"""
    raise HTTPException(status_code=400,detail="boom")

# ========================================
# 🔬 依赖注入共享实验
# ========================================
# 实验2: 验证同一请求中依赖实例是否共享
def dep_a(db:Session=Depends(get_db)):
    """依赖A - 获取数据库会话"""
    print(f"[dep_a] db_id={id(db)}")
    return db

def dep_b(db:Session=Depends(get_db)):
    """依赖B - 获取数据库会话"""
    print(f"[dep_b] db_id={id(db)}")
    return db

@app.get("/debug/dep-share")
def dep_share(
    a: Session=Depends(dep_a,use_cache=False),
    b: Session=Depends(dep_b,use_cache=False),
):
    """验证依赖实例共享 - 即使use_cache=False也共享"""
    print(f"[route] a_id={id(a)} b_id={id(b)} same={a is b}")
    return {"a_id":id(a),"b_id":id(b),"same":a is b}

# ========================================
# 💳 事务管理实验
# ========================================
# 实验3: 验证自动事务提交和回滚
@app.post("/debug/tx-ok")
def tx_ok(db:Session=Depends(get_db_tx)):
    """测试事务自动提交 - 成功案例"""
    db.add(TodoDB(title="tx ok",done=False))
    # get_db_tx 会在yield后自动commit
    return {"msg":"created"}

@app.post("/debug/tx-fail")
def tx_fail(db:Session=Depends(get_db_tx)):
    """测试事务自动回滚 - 失败案例"""
    db.add(TodoDB(title="tx fail",done=False))
    # 抛出异常会触发get_db_tx的rollback
    raise HTTPException(status_code=400,detail="force fail")
