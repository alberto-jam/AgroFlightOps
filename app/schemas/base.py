"""Base schemas and generic paginated response."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class TimestampMixin(BaseModel):
    """Mixin for created_at/updated_at fields."""

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
