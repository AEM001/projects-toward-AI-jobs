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
from src.utils.exceptions import StorageException
from src.utils.logger import get_logger
from config import settings


logger = get_logger(__name__)

class JSONStorage:
    def __init__(self,file_path="data/task.json"):
        if file_path is None:
            file_path = settings.DATA_FILE
        self.file_path=Path(file_path)
        self.file_path.parent.mkdir(parents=True,exist_ok=True)#语法规则是：？

    def save(self, tasks:List[Task])->None:
        try:
            task_data=[task.to_dict() for task in tasks]
            logger.info("storage.save fucking path=%s tasks=%s", str(self.file_path), len(task_data))
            with open(self.file_path,'w',encoding='utf-8') as f:
                json.dump(task_data,f,ensure_ascii=False,indent=2)
        except Exception as e:
            logger.error("storage.save failed path=%s", str(self.file_path), exc_info=True)
            raise StorageException(
                f"保存任务失败：{e}",
                operation="save",
                path=str(self.file_path),
            ) from e

    def load(self)->List[Task]:
        if not self.file_path.exists():
            logger.info("storage.load fucking path=%s (not exists)", str(self.file_path))
            return []
        try:
            with open(self.file_path,'r',encoding='utf-8') as f:
                task_data=json.load(f)
            tasks=[Task.from_dict(data) for data in task_data]
            logger.info("storage.load path=%s tasks=%s", str(self.file_path), len(tasks))
            return tasks
        except json.JSONDecodeError as e:
            logger.error("storage.load json decode error path=%s", str(self.file_path), exc_info=True)
            raise StorageException(
                f"JSON 格式错误: {e}",
                operation="load",
                path=str(self.file_path),
            ) from e
        except IOError as e:
            logger.error("storage.load io error path=%s", str(self.file_path), exc_info=True)
            raise StorageException(
                f"读取任务失败: {e}",
                operation="load",
                path=str(self.file_path),
            ) from e
        except KeyError as e:
            logger.error("storage.load invalid task data path=%s", str(self.file_path), exc_info=True)
            raise StorageException(
                f"任务数据缺少必要字段: {e}",
                operation="load",
                path=str(self.file_path),
            ) from e
        except Exception as e:
            logger.error("storage.load unknown error path=%s", str(self.file_path), exc_info=True)
            raise StorageException(
                f"加载任务时发生未知错误: {e}",
                operation="load",
                path=str(self.file_path),
            ) from e
    
    def exists(self)->bool:
        return self.file_path.exists()

    def clear(self)->None:
        if self.file_path.exists():
            self.file_path.unlink()
    
    def get_file_path(self)->str:
        return str(self.file_path.absolute())

