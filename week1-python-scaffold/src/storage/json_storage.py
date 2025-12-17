"""
存储模块：
将task对象转换为json格式
将json转换为task对象
保存到文件
从文件中读取
异常处理

实现方式：一个类，有以上这些方法
"""
import json
from pathlib import Path
from typing import List,Optional
from src.models.task import Task

class JSONStorage:
    def __init__(self,file_path="data/task.json"):
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)#语法规则是：？

    def save(self, tasks:List[Task])->None:
        try:
            task_data=[task.to_dict() for task in tasks]
            with open(self.file_path,'w',encoding='utf-8') as f:
                json.dump(task_data,f,ensure_ascii=False,indent=2)
        except Exception as e:
            raise Exception(f"保存任务失败：{e}")

    def load(self)->List[Task]:
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path,'r',encoding='utf-8') as f:
                task_data=json.load(f)
            tasks=[Task.from_dict(data) for data in task_data]
            return tasks
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式错误: {e}")
        except IOError as e:
            raise IOError(f"读取任务失败: {e}")
        except KeyError as e:
            raise ValueError(f"任务数据缺少必要字段: {e}")
        except Exception as e:
            raise Exception(f"加载任务时发生未知错误: {e}")
    
    def exists(self)->bool:
        return self.file_path.exists()

    def clear(self)->None:
        if self.file_path.exists():
            self.file_path.unlink()
    
    def get_file_path(self)->str:
        return str(self.file_path.absolute())

