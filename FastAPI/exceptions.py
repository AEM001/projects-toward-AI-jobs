class TodoNotFoundException(Exception):
    """Business exception for when a todo is not found"""
    def __init__(self, todo_id: int):
        self.todo_id = todo_id
        super().__init__(f"Todo with id {todo_id} not found")


class TodoValidationException(Exception):
    """Business exception for validation errors"""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class DatabaseException(Exception):
    """Business exception for database errors"""
    def __init__(self, detail: str = "Database error occurred"):
        self.detail = detail
        super().__init__(detail)

