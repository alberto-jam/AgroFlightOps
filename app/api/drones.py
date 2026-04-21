"""API routes for Drone CRUD — restricted to Administrador."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import DroneStatus
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.drone import DroneCreate, DroneResponse, DroneUpdate
from app.services.drone_service import DroneService

router = APIRouter(
    prefix="/drones",
    tags=["Drones"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR"))],
)


@router.post("", response_model=DroneResponse, status_code=201)
async def create_drone(
    body: DroneCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new drone."""
    service = DroneService(db)
    return await service.create_drone(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[DroneResponse])
async def list_drones(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: DroneStatus | None = Query(None),
    modelo: str | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List drones with pagination and optional filters."""
    service = DroneService(db)
    result = await service.list_drones(
        page=page,
        page_size=page_size,
        status=status,
        modelo=modelo,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[DroneResponse.model_validate(d) for d in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{drone_id}", response_model=DroneResponse)
async def get_drone(
    drone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a drone by ID."""
    service = DroneService(db)
    return await service.get_drone(drone_id)


@router.put("/{drone_id}", response_model=DroneResponse)
async def update_drone(
    drone_id: int,
    body: DroneUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a drone."""
    service = DroneService(db)
    return await service.update_drone(drone_id, body, usuario_id=current_user.id)


@router.patch("/{drone_id}", response_model=DroneResponse)
async def patch_drone(
    drone_id: int,
    body: DroneUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a drone."""
    service = DroneService(db)
    return await service.update_drone(drone_id, body, usuario_id=current_user.id)


@router.delete("/{drone_id}", response_model=DroneResponse)
async def delete_drone(
    drone_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a drone (set ativo=False)."""
    service = DroneService(db)
    return await service.delete_drone(drone_id, usuario_id=current_user.id)
