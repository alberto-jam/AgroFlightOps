"""Shared test fixtures — async SQLite in-memory DB, test client, auth tokens."""

from collections.abc import AsyncGenerator

import hypothesis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.models import Perfil, Usuario

# ---------------------------------------------------------------------------
# Hypothesis profiles
# ---------------------------------------------------------------------------
hypothesis.settings.register_profile("ci", max_examples=100)
hypothesis.settings.register_profile("dev", max_examples=30)
hypothesis.settings.register_profile("default", max_examples=50)
hypothesis.settings.load_profile("default")

# ---------------------------------------------------------------------------
# Async engine / session for tests (SQLite in-memory via aiosqlite)
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def _patch_bigint_for_sqlite():
    """Replace BigInteger with Integer in column definitions for SQLite compatibility.

    SQLite only auto-increments INTEGER PRIMARY KEY columns, not BIGINT.
    This patches the metadata so that all BigInteger PKs become Integer.
    """
    from sqlalchemy import Integer as SaInteger

    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, BigInteger):
                column.type = SaInteger()


from sqlalchemy import BigInteger  # noqa: E402

_patch_bigint_for_sqlite()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def test_engine():
    """Create a fresh async engine per test with all tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session bound to the test engine."""
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture()
async def async_client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX AsyncClient wired to the FastAPI app with DB override."""
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed profiles used by helper fixtures
# ---------------------------------------------------------------------------
PERFIS_SEED = [
    "ADMINISTRADOR",
    "COORDENADOR_OPERACIONAL",
    "PILOTO",
    "TECNICO",
    "FINANCEIRO",
]


async def _ensure_perfis(session: AsyncSession) -> dict[str, int]:
    """Insert seed profiles if missing and return {nome: id} mapping."""
    from sqlalchemy import select

    result = await session.execute(select(Perfil))
    existing = {p.nome: p.id for p in result.scalars().all()}
    for nome in PERFIS_SEED:
        if nome not in existing:
            perfil = Perfil(nome=nome, descricao=f"Perfil {nome}", ativo=True)
            session.add(perfil)
            await session.flush()
            existing[nome] = perfil.id
    await session.commit()
    return existing


async def _create_user_with_token(
    session: AsyncSession,
    perfil_map: dict[str, int],
    perfil_nome: str,
    email: str,
) -> str:
    """Create a user and return a valid JWT token."""
    # Use a pre-computed bcrypt hash for "test123456" to avoid passlib/bcrypt
    # version compatibility issues in the test environment.
    # If hash_password works, use it; otherwise fall back to a static hash.
    try:
        from app.core.security import hash_password
        senha_hash = hash_password("test123456")
    except Exception:
        # Pre-computed bcrypt hash for "test123456"
        senha_hash = "$2b$12$LJ3m4ys3Lk0TSwMCkVc8aOY1lVbwIprExQlaYROwJOsUlYKMaBSvS"

    user = Usuario(
        nome=f"Test {perfil_nome}",
        email=email,
        senha_hash=senha_hash,
        perfil_id=perfil_map[perfil_nome],
        ativo=True,
    )
    session.add(user)
    await session.flush()
    await session.commit()
    return create_access_token(
        usuario_id=user.id, perfil=perfil_nome, email=email
    )


@pytest.fixture()
async def admin_token(db_session: AsyncSession) -> str:
    perfil_map = await _ensure_perfis(db_session)
    return await _create_user_with_token(
        db_session, perfil_map, "ADMINISTRADOR", "admin@test.com"
    )


@pytest.fixture()
async def piloto_token(db_session: AsyncSession) -> str:
    perfil_map = await _ensure_perfis(db_session)
    return await _create_user_with_token(
        db_session, perfil_map, "PILOTO", "piloto@test.com"
    )


@pytest.fixture()
async def tecnico_token(db_session: AsyncSession) -> str:
    perfil_map = await _ensure_perfis(db_session)
    return await _create_user_with_token(
        db_session, perfil_map, "TECNICO", "tecnico@test.com"
    )


@pytest.fixture()
async def financeiro_token(db_session: AsyncSession) -> str:
    perfil_map = await _ensure_perfis(db_session)
    return await _create_user_with_token(
        db_session, perfil_map, "FINANCEIRO", "financeiro@test.com"
    )


@pytest.fixture()
async def coordenador_token(db_session: AsyncSession) -> str:
    perfil_map = await _ensure_perfis(db_session)
    return await _create_user_with_token(
        db_session, perfil_map, "COORDENADOR_OPERACIONAL", "coord@test.com"
    )
