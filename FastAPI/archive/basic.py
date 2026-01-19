from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Simple Notes API")

# ========== 1. 内存“数据库” ==========
notes = []
next_id = 1


# ========== 2. 数据模型（请求体 & 返回体） ==========
class NoteCreate(BaseModel):
    text: str = Field(min_length=1, description="Note text, cannot be empty")


class Note(BaseModel):
    id: int
    text: str


# ========== 3. 路由 ==========
@app.get("/health")
def health():
    return {"ok": True}

# response_model=Note是在返回一个固定的Note格式的数据
@app.post("/notes", response_model=Note, status_code=201)
def create_note(just_name: NoteCreate):#输入校验，必须是NoteCreate格式的数据
    global next_id

    new_note = {
        "id": next_id,
        "text": just_name.text,
        "test":"more response than difined Note"

    }
    notes.append(new_note)
    next_id += 1

    return new_note
# NoteCreate：我允许你传什么

# Note：我保证返回什么

@app.get("/notes", response_model=list[Note])
def list_notes():
    return notes

@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}

from fastapi import HTTPException

@app.get("/notes/{id}", response_model=Note)
def get_n(id:int):
    for i in notes:
        if i["id"]==id:
            return i

    raise HTTPException(status_code=404, detail="Note not found")

class NoteUpdate(BaseModel):
    text:str | None=None
# patch是部分更新，给什么更新什么，所以text可以是none

@app.patch("/notes/{id}",response_model=Note)
def update_note(id:int,update:NoteUpdate):
    for i in notes:
        if i["id"]==id:
            if update.text is not None:
                i["text"]=update.text
            return i

    raise HTTPException(status_code=404,detail="Note not found")

@app.delete("/notes/{id}",status_code=204)
def delete_note(id:int):
    for index,note in enumerate(notes):
        if note["id"]==id:
            notes.pop(index)
            return
    raise HTTPException(status_code=404,detail="Note not found")