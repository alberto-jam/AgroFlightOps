"""Generic base repository with CRUD operations and pagination."""

import math
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.core.exceptions import EntityNotFoundError

ModelType = TypeVar("ModelType", bound=Base)


class PaginatedResult(Generic[ModelType]):
    """Container for paginated query results."""

    def __init__(
        self,
        items: list[ModelType],
        total: int,
        page: int,
        page_size: int,
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.pages = math.ceil(total / page_size) if page_size > 0 else 0


class BaseRepository(Generic[ModelType]):
    """Generic repository providing CRUD and paginated listing."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> ModelType:
        """Get a record by ID. Raises EntityNotFoundError if not found."""
        result = await self.db.get(self.model, id)
        if result is None:
            raise EntityNotFoundError(
                f"{self.model.__tablename__} com id={id} não encontrado"
            )
        return result

    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: list[Any] | None = None,
        order_by: Any | None = None,
    ) -> PaginatedResult[ModelType]:
        """List records with pagination.

        Args:
            page: Page number (1-indexed). Default 1.
            page_size: Items per page. Default 20, max 100.
            filters: List of SQLAlchemy filter expressions.
            order_by: Column or expression to order by.
        """
        # Clamp page_size
        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        # Base query
        query: Select = select(self.model)

        if filters:
            for f in filters:
                query = query.where(f)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply ordering
        if order_by is not None:
            query = query.order_by(order_by)
        else:
            # Default order by id
            query = query.order_by(self.model.id)  # type: ignore[attr-defined]

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def update(self, id: int, **kwargs: Any) -> ModelType:
        """Update a record by ID. Raises EntityNotFoundError if not found."""
        instance = await self.get_by_id(id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def soft_delete(self, id: int) -> ModelType:
        """Soft-delete a record by setting ativo=False."""
        instance = await self.get_by_id(id)
        instance.ativo = False  # type: ignore[attr-defined]
        await self.db.flush()
        await self.db.refresh(instance)
        return instance
