from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from slowapi import Limiter

from src.api.deps import get_db, get_db_tx, get_current_user, limiter
from src.schemas.todo import TodoCreate, Todo, TodoUpdate, TodoListResponse
from src.schemas.pagination import PaginationParams
from src.services.todo_service import create_todo_service, list_todos_service, get_todo_service, update_todo_service, delete_todo_service
from src.schemas.user import User
from src.utils.email import send_todo_created_email

router = APIRouter()

@router.post("/todos", 
          response_model=Todo, 
          status_code=201, 
          summary="Create a new TODO task",
          description="""
Create a new TODO task with the provided information.

The task will be created with a default status of 'pending' and current timestamp."""
          )
@limiter.limit("200/minute")
def create_todo(request: Request, todo: TodoCreate, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_tx)):
    # Create the todo
    result = create_todo_service(db, todo,current_user.id)
    
    # Add background task to send email notification
    background_tasks.add_task(
        send_todo_created_email, 
        user_email=current_user.email, 
        todo_title=result.title, 
        todo_ddl=result.ddl
    )
    
    return result


@router.get("/todos", response_model=TodoListResponse, tags=["Todos"], 
           summary="List all TODO tasks with pagination and filtering",
           description="""
Retrieve a paginated list of all TODO tasks in the system with optional filtering.
 
**Query Parameters:**
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 10, max: 100)
- `title`: Search by title (partial match)
- `filter_today`: Show only todos due today (default: false)
- `filter_week`: Show only todos due within the next 7 days (default: false)
 
**Returns:** Paginated list with metadata including total count, current page, etc.
"""
# responses={
#     200: {
#         "description": "Paginated and filtered list of todos",
#         "content": {
#             "application/json": {
#                 "example": {
#                     "items": [
#                         {"id": 1, "title": "Buy groceries", "ddl": "2026-02-10 12:00", "done": False}
#                     ],
#                     "total": 5,
#                     "skip": 0,
#                     "limit": 10,
#                     "page": 0,
#                     "pages": 1
#                 }
#             }
#         }
#     }
# }
)
@limiter.limit("100/minute")
def list_todos(request: Request, Pagination: PaginationParams=Depends(),current_user:User=Depends(get_current_user),db: Session = Depends(get_db)):
    return list_todos_service(
        db,skip=Pagination.skip,limit=Pagination.limit,
        title=Pagination.title,
        filter_today=Pagination.filter_today,
        filter_week=Pagination.filter_week,
        sort_by=Pagination.sort_by.value,
        sort_order=Pagination.sort_order.value,
        user_id=current_user.id)

@router.get("/todos/{id}", response_model=Todo,tags=["Todos"],summary="Get a specific TODO task",
 description="""
Retrieve a single TODO task by its unique identifier.
 
**Path Parameters:**
- `id`: The unique identifier of the todo task
 
**Returns:** The complete todo object if found
""",
         responses={
             200: {
                 "description": "Todo found",
                 "content": {
                     "application/json": {
                         "example": {
                             "id": 1,
                             "title": "Learn FastAPI",
                             "description": "Complete tutorial",
                             "status": "pending",
                             "created_at": "2024-01-01T12:00:00",
                             "updated_at": "2024-01-01T12:00:00"
                         }
                     }
                 }
             },
             404: {
                 "description": "Todo not found",
                 "content": {
                     "application/json": {
                         "example": {"detail": "Todo with id 1 not found"}
                     }
                 }
             }
         })
def get_todo(id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    return get_todo_service(db, id,current_user.id)

@router.put("/todos/{id}", response_model=Todo, tags=["Todos"], summary="Update an existing TODO task",
description="""
Update an existing TODO task with new information.

**Path Parameters:**
- `id`: The unique identifier of the todo task

**Request Body:**
- `update`: Partial update data for the todo (title, description, status)

**Returns:** The updated todo object
""",
responses={
    200: {
        "description": "Todo updated successfully",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "title": "Learn FastAPI",
                    "description": "Complete tutorial",
                    "status": "completed",
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:30:00"
                }
            }
        }
    },
    404: {
        "description": "Todo not found",
        "content": {
            "application/json": {
                "example": {"detail": "Todo with id 1 not found"}
            }
        }
    }
})
def update_todo(id: int, update: TodoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_tx)):
    return update_todo_service(db, id, update, current_user.id)

@router.delete("/todos/{id}", status_code=204, tags=["Todos"], summary="Delete a TODO task",
description="""
Delete a TODO task by its unique identifier.

**Path Parameters:**
- `id`: The unique identifier of the todo task to delete

This operation cannot be undone.
""",
responses={
    204: {
        "description": "Todo deleted successfully"
    },
    404: {
        "description": "Todo not found",
        "content": {
            "application/json": {
                "example": {"detail": "Todo with id 1 not found"}
            }
        }
    }
})
def delete_todo(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db_tx)):
    delete_todo_service(db, id, current_user.id)
