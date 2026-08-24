"""Integration tests for the GET /medicoes-rop endpoint.

Tests the full flow: create entities via SQLAlchemy → query the endpoint → verify results.

Validates Requirements: 3.1, 3.2, 3.5, 4.1, 4.3
"""

from datetime import date, datetime, time
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import (
    Cliente,
    Cultura,
    Drone,
    Missao,
    OrdemServico,
    Perfil,
    Propriedade,
    Talhao,
    Usuario,
)


# ---------------------------------------------------------------------------
# Helper: create full entity chain needed for a Missao
# ---------------------------------------------------------------------------


async def _create_base_entities(session: AsyncSession) -> dict:
    """Create minimal entity chain: perfil → usuario (piloto) → cliente → propriedade → cultura → talhao → drone.

    Returns a dict with all created entities for reuse.
    """
    # Ensure PILOTO perfil exists
    from sqlalchemy import select

    result = await session.execute(select(Perfil).where(Perfil.nome == "PILOTO"))
    perfil_piloto = result.scalar_one_or_none()
    if not perfil_piloto:
        perfil_piloto = Perfil(nome="PILOTO", descricao="Piloto", ativo=True)
        session.add(perfil_piloto)
        await session.flush()

    # Piloto user
    piloto = Usuario(
        nome="Piloto Test",
        email="piloto_integ@test.com",
        senha_hash="$2b$12$LJ3m4ys3Lk0TSwMCkVc8aOY1lVbwIprExQlaYROwJOsUlYKMaBSvS",
        perfil_id=perfil_piloto.id,
        ativo=True,
    )
    session.add(piloto)
    await session.flush()

    # Cliente
    cliente = Cliente(nome="Cliente Integração", ativo=True)
    session.add(cliente)
    await session.flush()

    # Propriedade
    propriedade = Propriedade(
        cliente_id=cliente.id,
        nome="Fazenda Teste",
        municipio="Uberlândia",
        estado="MG",
        area_total=Decimal("100.00"),
        ativo=True,
    )
    session.add(propriedade)
    await session.flush()

    # Cultura
    cultura = Cultura(nome="Soja Integração", ativo=True)
    session.add(cultura)
    await session.flush()

    # Talhão
    talhao = Talhao(
        propriedade_id=propriedade.id,
        nome="Talhão A",
        area_hectares=Decimal("50.00"),
        cultura_id=cultura.id,
        ativo=True,
    )
    session.add(talhao)
    await session.flush()

    # Drone
    drone = Drone(
        identificacao="DRONE-INTEG-001",
        modelo="DJI T30",
        capacidade_litros=Decimal("30.00"),
        status="DISPONIVEL",
        horas_voadas=Decimal("0.00"),
        ativo=True,
    )
    session.add(drone)
    await session.flush()

    await session.commit()

    return {
        "cliente": cliente,
        "propriedade": propriedade,
        "cultura": cultura,
        "talhao": talhao,
        "drone": drone,
        "piloto": piloto,
    }


async def _create_ordem_servico(
    session: AsyncSession,
    cliente_id: int,
    propriedade_id: int,
    talhao_id: int,
    cultura_id: int,
    criado_por: int,
    codigo: str = "OS-INTEG-001",
) -> OrdemServico:
    """Create a minimal OrdemServico."""
    os = OrdemServico(
        codigo=codigo,
        cliente_id=cliente_id,
        propriedade_id=propriedade_id,
        talhao_id=talhao_id,
        cultura_id=cultura_id,
        tipo_aplicacao="Pulverização",
        prioridade="MEDIA",
        data_prevista=date(2024, 6, 15),
        status="APROVADA",
        criado_por=criado_por,
    )
    session.add(os)
    await session.flush()
    return os


async def _create_missao(
    session: AsyncSession,
    ordem_servico_id: int,
    piloto_id: int,
    drone_id: int,
    codigo: str = "MIS-INTEG-001",
    encerrado_tecnicamente_em: datetime | None = None,
    medicao_enviada_em: datetime | None = None,
) -> Missao:
    """Create a minimal Missao with configurable encerrado/medicao timestamps."""
    missao = Missao(
        codigo=codigo,
        ordem_servico_id=ordem_servico_id,
        piloto_id=piloto_id,
        drone_id=drone_id,
        data_agendada=date(2024, 6, 15),
        hora_agendada=time(8, 0),
        area_prevista=Decimal("50.00"),
        volume_previsto=Decimal("100.000"),
        status="ENCERRADA_TECNICAMENTE",
        encerrado_tecnicamente_em=encerrado_tecnicamente_em,
        medicao_enviada_em=medicao_enviada_em,
    )
    session.add(missao)
    await session.flush()
    return missao


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_flow_returns_eligible_mission(async_client, db_session, admin_token):
    """Full chain: create cliente → prop → talhão → OS → missão (encerrada, sem medição) → GET returns it.

    Validates Requirements 3.1, 3.2, 4.1
    """
    entities = await _create_base_entities(db_session)

    os = await _create_ordem_servico(
        db_session,
        cliente_id=entities["cliente"].id,
        propriedade_id=entities["propriedade"].id,
        talhao_id=entities["talhao"].id,
        cultura_id=entities["cultura"].id,
        criado_por=entities["piloto"].id,
    )

    missao = await _create_missao(
        db_session,
        ordem_servico_id=os.id,
        piloto_id=entities["piloto"].id,
        drone_id=entities["drone"].id,
        encerrado_tecnicamente_em=datetime(2024, 6, 20, 14, 30, 0),
        medicao_enviada_em=None,
    )
    await db_session.commit()

    response = await async_client.get(
        "/medicoes-rop",
        params={
            "cliente_id": entities["cliente"].id,
            "data_inicial": "2024-06-01",
            "data_final": "2024-06-30",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    # Find the mission we created
    found = [item for item in data["items"] if item["id"] == missao.id]
    assert len(found) == 1

    item = found[0]
    assert item["codigo"] == "MIS-INTEG-001"
    assert item["propriedade_nome"] == "Fazenda Teste"
    assert item["talhao_nome"] == "Talhão A"
    assert item["encerrado_tecnicamente_em"] is not None
    assert item["status"] == "ENCERRADA_TECNICAMENTE"


@pytest.mark.asyncio
async def test_empty_response_when_no_eligible_missions(async_client, db_session, admin_token):
    """Query a date range with no missions → returns {items: [], total: 0}.

    Validates Requirements 3.5
    """
    entities = await _create_base_entities(db_session)

    # No missions created — just query
    response = await async_client.get(
        "/medicoes-rop",
        params={
            "cliente_id": entities["cliente"].id,
            "data_inicial": "2030-01-01",
            "data_final": "2030-12-31",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_excludes_already_measured_missions(async_client, db_session, admin_token):
    """Mission with medicao_enviada_em set should NOT appear in results.

    Validates Requirements 3.2
    """
    entities = await _create_base_entities(db_session)

    os = await _create_ordem_servico(
        db_session,
        cliente_id=entities["cliente"].id,
        propriedade_id=entities["propriedade"].id,
        talhao_id=entities["talhao"].id,
        cultura_id=entities["cultura"].id,
        criado_por=entities["piloto"].id,
        codigo="OS-EXCL-001",
    )

    # Mission already measured
    await _create_missao(
        db_session,
        ordem_servico_id=os.id,
        piloto_id=entities["piloto"].id,
        drone_id=entities["drone"].id,
        codigo="MIS-ALREADY-MEASURED",
        encerrado_tecnicamente_em=datetime(2024, 7, 10, 10, 0, 0),
        medicao_enviada_em=datetime(2024, 7, 15, 9, 0, 0),
    )
    await db_session.commit()

    response = await async_client.get(
        "/medicoes-rop",
        params={
            "cliente_id": entities["cliente"].id,
            "data_inicial": "2024-07-01",
            "data_final": "2024-07-31",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    # The already-measured mission should be excluded
    ids = [item["id"] for item in data["items"]]
    measured_mission_codes = [
        item["codigo"] for item in data["items"] if item["codigo"] == "MIS-ALREADY-MEASURED"
    ]
    assert measured_mission_codes == []


@pytest.mark.asyncio
async def test_pagination_with_multiple_missions(async_client, db_session, admin_token):
    """Create multiple eligible missions → verify page/page_size/total/pages metadata.

    Validates Requirements 4.3
    """
    entities = await _create_base_entities(db_session)

    os = await _create_ordem_servico(
        db_session,
        cliente_id=entities["cliente"].id,
        propriedade_id=entities["propriedade"].id,
        talhao_id=entities["talhao"].id,
        cultura_id=entities["cultura"].id,
        criado_por=entities["piloto"].id,
        codigo="OS-PAG-001",
    )

    # Create 5 eligible missions
    for i in range(5):
        await _create_missao(
            db_session,
            ordem_servico_id=os.id,
            piloto_id=entities["piloto"].id,
            drone_id=entities["drone"].id,
            codigo=f"MIS-PAG-{i:03d}",
            encerrado_tecnicamente_em=datetime(2024, 8, 10 + i, 10, 0, 0),
            medicao_enviada_em=None,
        )
    await db_session.commit()

    # Request page 1, page_size=2
    response = await async_client.get(
        "/medicoes-rop",
        params={
            "cliente_id": entities["cliente"].id,
            "data_inicial": "2024-08-01",
            "data_final": "2024-08-31",
            "page": 1,
            "page_size": 2,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["pages"] == 3  # ceil(5/2) = 3
    assert len(data["items"]) == 2

    # Request page 3 → should have 1 item
    response2 = await async_client.get(
        "/medicoes-rop",
        params={
            "cliente_id": entities["cliente"].id,
            "data_inicial": "2024-08-01",
            "data_final": "2024-08-31",
            "page": 3,
            "page_size": 2,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["total"] == 5
    assert data2["page"] == 3
    assert data2["page_size"] == 2
    assert data2["pages"] == 3
    assert len(data2["items"]) == 1
