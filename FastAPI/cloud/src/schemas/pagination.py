from enum import Enum
from pydantic import BaseModel, Field

class SortField(str, Enum):
    id = "id"
    ddl = "ddl"
    title = "title"
    done = "done"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of items to return")
    title: str | None = Field(default=None, description="Search by title (partial match)")
    filter_today: bool = Field(default=False, description="Show only todos due today")
    filter_week: bool = Field(default=False, description="Show only todos due within the next 7 days")

    sort_by: SortField = Field(default=SortField.ddl, description="Sort by field")
    sort_order: SortOrder = Field(default=SortOrder.asc, description="Sort order")

class PaginatedResponse(BaseModel):
    """Base pagination response metadata"""
    total: int = Field(description="Total number of items")
    skip: int = Field(description="Number of items skipped")
    limit: int = Field(description="Number of items per page")
    page: int = Field(description="Current page number (0-based)")
    pages: int = Field(description="Total number of pages")