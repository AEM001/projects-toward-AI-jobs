from typing import List
from sqlmodel import Session, select
from models import Task, User
from schemas import TaskCreate, TaskUpdate


def create_task(session: Session, task: TaskCreate, user_id: int) -> Task:
    """创建任务"""
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status or "pending",
        user_id=user_id
    )
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def get_tasks_by_user(session: Session, user_id: int) -> List[Task]:
    """获取用户的所有任务"""
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    results = session.exec(statement)
    return list(results)


def get_task(session: Session, task_id: int, user_id: int) -> Task:
    """获取单个任务"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()


def update_task(session: Session, task_id: int, user_id: int, task_update: TaskUpdate) -> Task:
    """更新任务"""
    db_task = get_task(session, task_id, user_id)
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """删除任务"""
    db_task = get_task(session, task_id, user_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True
