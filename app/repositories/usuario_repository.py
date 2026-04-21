"""Repository for Usuario entity with email uniqueness check."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import Usuario
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """Usuario repository extending BaseRepository with email lookup."""

    def __init__(self, db: AsyncSession):
        super().__init__(Usuario, db)

    async def get_by_email(self, email: str) -> Usuario | None:
        """Find a user by email. Returns None if not found."""
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Usuario:
        """Create a user, raising DuplicateEntityError if email already exists."""
        existing = await self.get_by_email(kwargs.get("email", ""))
        if existing:
            raise DuplicateEntityError("Email já cadastrado")
        return await super().create(**kwargs)
