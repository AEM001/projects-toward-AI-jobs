from enum import Enum
from datetime import datetime

class Status(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Priority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task:
    def __init__(self,id,title,priority=Priority.MEDIUM,status=Status.PENDING,created_at=datetime.now(),updated_at=datetime.now()):
        self.id=id
        self.title=title
        self.priority=priority
        self.status=status
        self.created_at=created_at
        self.updated_at=updated_at
    
    def to_dict(self):
        return{
            "id":self.id,
            "title":self.title,
            "priority":self.priority.value,
            "status":self.status.value,
            "created_at":self.created_at.isoformat(),
            "updated_at":self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls,data:dict)->"Task":
        return cls(
            id=data["id"],
            title=data["title"],
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]))

    def update_status(self,new_status:Status)->None:
        self.status=new_status
        self.updated_at=datetime.now()
    
    def __str__(self):
        return f"Task({self.id}): {self.title} [{self.status.name}]"