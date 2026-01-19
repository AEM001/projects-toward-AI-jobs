from pydantic import BaseModel, Field, ConfigDict

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
