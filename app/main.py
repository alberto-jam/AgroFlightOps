"""AgroFlightOps Backend — FastAPI application with Mangum handler for AWS Lambda."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.core.config import settings
from app.core.exceptions import (
    BusinessRuleViolationError,
    DependencyActiveError,
    DuplicateEntityError,
    EntityNotFoundError,
    InsufficientStockError,
    InvalidStateTransitionError,
)

_root_path = f"/{settings.APP_ENV}" if settings.APP_ENV else ""

app = FastAPI(
    title="AgroFlightOps API",
    description="API para gestão de operações de pulverização agrícola com drones",
    version="1.0.0",
    root_path=_root_path,
)

# Parse CORS origins from settings — supports comma-separated list or "*"
_raw_origins = settings.CORS_ORIGINS.strip()
if _raw_origins == "*":
    _allow_origins: list[str] = ["*"]
else:
    _allow_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# CORS middleware — allows frontend S3 requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message, "errors": []},
    )


@app.exception_handler(DuplicateEntityError)
async def duplicate_entity_handler(request: Request, exc: DuplicateEntityError):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "errors": []},
    )


@app.exception_handler(InvalidStateTransitionError)
async def invalid_state_transition_handler(
    request: Request, exc: InvalidStateTransitionError
):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "errors": []},
    )


@app.exception_handler(DependencyActiveError)
async def dependency_active_handler(request: Request, exc: DependencyActiveError):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message, "errors": []},
    )


@app.exception_handler(BusinessRuleViolationError)
async def business_rule_violation_handler(
    request: Request, exc: BusinessRuleViolationError
):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message, "errors": exc.errors},
    )


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.message, "errors": []},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for Pydantic validation errors.

    Formats the response as {"detail": "...", "errors": [...]} to match
    the standard error response format defined in the design document.
    """
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        # Build field name from location, skipping 'body' prefix
        field_parts = [str(part) for part in loc if part != "body"]
        field = ".".join(field_parts) if field_parts else "unknown"
        errors.append({"field": field, "message": error.get("msg", "Valor inválido")})

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação nos dados enviados",
            "errors": errors,
        },
    )


# ============================================================================
# Routes
# ============================================================================

from app.api.auth import router as auth_router  # noqa: E402
from app.api.baterias import router as baterias_router  # noqa: E402
from app.api.checklists import router as checklists_router  # noqa: E402
from app.api.clientes import router as clientes_router  # noqa: E402
from app.api.culturas import router as culturas_router  # noqa: E402
from app.api.drones import router as drones_router  # noqa: E402
from app.api.insumos import router as insumos_router  # noqa: E402
from app.api.missoes import router as missoes_router  # noqa: E402
from app.api.financeiro import router as financeiro_router  # noqa: E402
from app.api.evidencias import router as evidencias_router  # noqa: E402
from app.api.ocorrencias import router as ocorrencias_router  # noqa: E402
from app.api.ordens_servico import router as ordens_servico_router  # noqa: E402
from app.api.propriedades import router as propriedades_router  # noqa: E402
from app.api.talhoes import router as talhoes_router  # noqa: E402
from app.api.manutencoes import router as manutencoes_router  # noqa: E402
from app.api.documentos_oficiais import router as documentos_oficiais_router  # noqa: E402
from app.api.auditoria import router as auditoria_router  # noqa: E402
from app.api.relatorios import router as relatorios_router  # noqa: E402
from app.api.tipos_ocorrencia import router as tipos_ocorrencia_router  # noqa: E402
from app.api.itens_checklist_padrao import router as itens_checklist_padrao_router  # noqa: E402
from app.api.usuarios import router as usuarios_router  # noqa: E402
from app.api.telemetria import router as telemetria_router  # noqa: E402
from app.api.insights import router as insights_router  # noqa: E402

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(clientes_router)
app.include_router(culturas_router)
app.include_router(propriedades_router)
app.include_router(talhoes_router)
app.include_router(drones_router)
app.include_router(baterias_router)
app.include_router(insumos_router)
app.include_router(ordens_servico_router)
app.include_router(missoes_router)
app.include_router(financeiro_router)
app.include_router(ocorrencias_router)
app.include_router(evidencias_router)
app.include_router(checklists_router)
app.include_router(manutencoes_router)
app.include_router(documentos_oficiais_router)
app.include_router(auditoria_router)
app.include_router(relatorios_router)
app.include_router(tipos_ocorrencia_router)
app.include_router(itens_checklist_padrao_router)
app.include_router(telemetria_router)
app.include_router(insights_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Mangum handler for AWS Lambda + API Gateway
# api_gateway_base_path strips the stage prefix (e.g. "/dev") from the path
_base_path = f"/{settings.APP_ENV}" if settings.APP_ENV else ""
handler = Mangum(app, lifespan="off", api_gateway_base_path=_base_path)
