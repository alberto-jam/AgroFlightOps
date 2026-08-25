"""Integration tests for Gestão de Relatórios de Medição endpoints.

Tests the full flow: generate report → list → download → send → delete → verify missions eligible.

Validates Requirements: 2.1, 3.1, 4.1, 5.1
"""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from unittest.mock import MagicMock, patch

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
    RelatorioMedicao,
    RelatorioMedicaoMissao,
    Talhao,
    Usuario,
)


# ---------------------------------------------------------------------------
# Helpers — create entity chains for integration tests
# ---------------------------------------------------------------------------


async def _seed_base_entities(session: AsyncSession) -> dict:
    """Create a full entity chain: perfil → usuario → cliente → prop → cultura → talhao → drone.

    Returns dict with all entities.
    """
    from sqlalchemy import select

    # Ensure ADMINISTRADOR perfil exists
    result = await session.execute(select(Perfil).where(Perfil.nome == "ADMINISTRADOR"))
    perfil_admin = result.scalar_one_or_none()
    if not perfil_admin:
        perfil_admin = Perfil(nome="ADMINISTRADOR", descricao="Admin", ativo=True)
        session.add(perfil_admin)
        await session.flush()

    # Ensure PILOTO perfil exists
    result = await session.execute(select(Perfil).where(Perfil.nome == "PILOTO"))
    perfil_piloto = result.scalar_one_or_none()
    if not perfil_piloto:
        perfil_piloto = Perfil(nome="PILOTO", descricao="Piloto", ativo=True)
        session.add(perfil_piloto)
        await session.flush()

    # Admin user (also used as gerado_por)
    admin = Usuario(
        nome="Admin Gestao",
        email="admin_gestao@test.com",
        senha_hash="$2b$12$LJ3m4ys3Lk0TSwMCkVc8aOY1lVbwIprExQlaYROwJOsUlYKMaBSvS",
        perfil_id=perfil_admin.id,
        ativo=True,
    )
    session.add(admin)
    await session.flush()

    # Piloto user
    piloto = Usuario(
        nome="Piloto Gestao",
        email="piloto_gestao@test.com",
        senha_hash="$2b$12$LJ3m4ys3Lk0TSwMCkVc8aOY1lVbwIprExQlaYROwJOsUlYKMaBSvS",
        perfil_id=perfil_piloto.id,
        ativo=True,
    )
    session.add(piloto)
    await session.flush()

    # Cliente
    cliente = Cliente(nome="Cliente Relatório Teste", ativo=True)
    session.add(cliente)
    await session.flush()

    # Propriedade
    propriedade = Propriedade(
        cliente_id=cliente.id,
        nome="Fazenda Relatório",
        municipio="Uberlândia",
        estado="MG",
        area_total=Decimal("200.00"),
        ativo=True,
    )
    session.add(propriedade)
    await session.flush()

    # Cultura
    cultura = Cultura(nome="Soja Relatório", ativo=True)
    session.add(cultura)
    await session.flush()

    # Talhão
    talhao = Talhao(
        propriedade_id=propriedade.id,
        nome="Talhão Relatório A",
        area_hectares=Decimal("80.00"),
        cultura_id=cultura.id,
        ativo=True,
    )
    session.add(talhao)
    await session.flush()

    # Drone
    drone = Drone(
        identificacao="DRONE-REL-001",
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
        "admin": admin,
        "piloto": piloto,
        "cliente": cliente,
        "propriedade": propriedade,
        "cultura": cultura,
        "talhao": talhao,
        "drone": drone,
    }


async def _create_relatorio_with_missoes(
    session: AsyncSession,
    entities: dict,
    *,
    num_missoes: int = 3,
    status: str = "ATIVO",
    data_inicial: date = date(2024, 6, 1),
    data_final: date = date(2024, 6, 30),
    s3_key: str = "MEDICAO/cliente/Medicao_20240601_20240630.pdf",
) -> tuple:
    """Create a RelatorioMedicao with linked missions.

    Returns (relatorio, missoes).
    """
    # Create OrdemServico
    unique_id = uuid.uuid4().hex[:8]
    os = OrdemServico(
        codigo=f"OS-REL-{unique_id}",
        cliente_id=entities["cliente"].id,
        propriedade_id=entities["propriedade"].id,
        talhao_id=entities["talhao"].id,
        cultura_id=entities["cultura"].id,
        tipo_aplicacao="Pulverização",
        prioridade="MEDIA",
        data_prevista=date(2024, 6, 15),
        status="APROVADA",
        criado_por=entities["admin"].id,
    )
    session.add(os)
    await session.flush()

    # Create missions
    missoes = []
    total_area = Decimal("0")
    for i in range(num_missoes):
        area = Decimal(f"{20 + i * 10}.50")
        total_area += area
        missao = Missao(
            codigo=f"MIS-REL-{unique_id}-{i:03d}",
            ordem_servico_id=os.id,
            piloto_id=entities["piloto"].id,
            drone_id=entities["drone"].id,
            data_agendada=date(2024, 6, 10 + i),
            hora_agendada=time(8, 0),
            area_prevista=area,
            area_realizada=area,
            volume_previsto=Decimal("100.000"),
            status="ENCERRADA_TECNICAMENTE",
            encerrado_tecnicamente_em=datetime(2024, 6, 15 + i, 14, 0, 0),
            medicao_enviada_em=datetime(2024, 6, 20, 10, 0, 0),
        )
        session.add(missao)
        missoes.append(missao)
    await session.flush()

    # Create RelatorioMedicao
    relatorio = RelatorioMedicao(
        cliente_id=entities["cliente"].id,
        s3_key=s3_key,
        data_inicial=data_inicial,
        data_final=data_final,
        total_area=total_area,
        qtd_missoes=num_missoes,
        gerado_em=datetime(2024, 6, 25, 12, 0, 0),
        gerado_por=entities["admin"].id,
        status=status,
    )
    session.add(relatorio)
    await session.flush()

    # Create junction records
    for missao in missoes:
        junction = RelatorioMedicaoMissao(
            relatorio_id=relatorio.id,
            missao_id=missao.id,
        )
        session.add(junction)
    await session.flush()

    await session.commit()

    return relatorio, missoes


# ---------------------------------------------------------------------------
# Tests: Listing endpoint (GET /medicoes-rop/relatorios)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_listar_relatorios_returns_active_by_default(
    async_client, db_session, admin_token
):
    """GET /medicoes-rop/relatorios without status filter returns only ATIVO reports.

    Validates Requirements: 2.1, 2.6
    """
    entities = await _seed_base_entities(db_session)
    await _create_relatorio_with_missoes(db_session, entities, status="ATIVO")
    await _create_relatorio_with_missoes(
        db_session, entities, status="EXCLUIDO",
        s3_key="MEDICAO/cliente/Medicao_excluido.pdf",
    )

    response = await async_client.get(
        "/medicoes-rop/relatorios",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # All returned items should be ATIVO
    for item in data["items"]:
        assert item["status"] == "ATIVO"


@pytest.mark.asyncio
async def test_listar_relatorios_filter_by_cliente(
    async_client, db_session, admin_token
):
    """GET /medicoes-rop/relatorios?cliente_id=X returns only that client's reports.

    Validates Requirements: 2.2
    """
    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"cliente_id": entities["cliente"].id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["cliente_nome"] == "Cliente Relatório Teste"


@pytest.mark.asyncio
async def test_listar_relatorios_filter_by_date_range(
    async_client, db_session, admin_token
):
    """GET /medicoes-rop/relatorios with date filters narrows results correctly.

    Validates Requirements: 2.3, 2.4
    """
    entities = await _seed_base_entities(db_session)
    await _create_relatorio_with_missoes(
        db_session, entities,
        data_inicial=date(2024, 6, 1),
        data_final=date(2024, 6, 30),
        s3_key="MEDICAO/cliente/Medicao_jun.pdf",
    )
    await _create_relatorio_with_missoes(
        db_session, entities,
        data_inicial=date(2024, 7, 1),
        data_final=date(2024, 7, 31),
        s3_key="MEDICAO/cliente/Medicao_jul.pdf",
    )

    # Filter data_inicial >= 2024-07-01
    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"data_inicial": "2024-07-01"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["data_inicial"] >= "2024-07-01"


@pytest.mark.asyncio
async def test_listar_relatorios_filter_by_status_excluido(
    async_client, db_session, admin_token
):
    """GET /medicoes-rop/relatorios?status=EXCLUIDO returns only deleted reports.

    Validates Requirements: 2.5
    """
    entities = await _seed_base_entities(db_session)
    await _create_relatorio_with_missoes(db_session, entities, status="ATIVO")
    await _create_relatorio_with_missoes(
        db_session, entities, status="EXCLUIDO",
        s3_key="MEDICAO/cliente/Medicao_excluido2.pdf",
    )

    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"status": "EXCLUIDO"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["status"] == "EXCLUIDO"


@pytest.mark.asyncio
async def test_listar_relatorios_pagination(
    async_client, db_session, admin_token
):
    """GET /medicoes-rop/relatorios supports pagination.

    Validates Requirements: 2.7
    """
    entities = await _seed_base_entities(db_session)
    # Create 3 reports
    for i in range(3):
        await _create_relatorio_with_missoes(
            db_session, entities,
            s3_key=f"MEDICAO/cliente/Medicao_pag_{i}.pdf",
            num_missoes=1,
        )

    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"page": 1, "page_size": 2},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2
    assert data["total"] >= 3
    assert data["pages"] >= 2


@pytest.mark.asyncio
async def test_listar_relatorios_ordered_by_gerado_em_desc(
    async_client, db_session, admin_token
):
    """Results are ordered by gerado_em descending (most recent first).

    Validates Requirements: 2.8
    """
    entities = await _seed_base_entities(db_session)
    await _create_relatorio_with_missoes(
        db_session, entities,
        s3_key="MEDICAO/cliente/Medicao_ord1.pdf",
        num_missoes=1,
    )
    await _create_relatorio_with_missoes(
        db_session, entities,
        s3_key="MEDICAO/cliente/Medicao_ord2.pdf",
        num_missoes=1,
    )

    response = await async_client.get(
        "/medicoes-rop/relatorios",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    items = data["items"]
    if len(items) >= 2:
        for i in range(len(items) - 1):
            assert items[i]["gerado_em"] >= items[i + 1]["gerado_em"]


# ---------------------------------------------------------------------------
# Tests: Download endpoint (GET /medicoes-rop/relatorios/{id}/download)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_download_relatorio_success(
    mock_boto_client, async_client, db_session, admin_token
):
    """GET /relatorios/{id}/download returns a presigned URL for active report.

    Validates Requirements: 3.1, 3.3
    """
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/presigned-url"
    mock_boto_client.return_value = mock_s3

    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.get(
        f"/medicoes-rop/relatorios/{relatorio.id}/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "download_url" in data
    assert data["download_url"] == "https://s3.example.com/presigned-url"


@pytest.mark.asyncio
async def test_download_relatorio_not_found(async_client, db_session, admin_token):
    """GET /relatorios/{id}/download with invalid id returns 404.

    Validates Requirements: 3.4
    """
    await _seed_base_entities(db_session)

    response = await async_client.get(
        "/medicoes-rop/relatorios/99999/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_relatorio_deleted_returns_404(
    async_client, db_session, admin_token
):
    """GET /relatorios/{id}/download for EXCLUIDO report returns 404.

    Validates Requirements: 3.5
    """
    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(
        db_session, entities, status="EXCLUIDO",
        s3_key="MEDICAO/cliente/Medicao_deleted.pdf",
    )

    response = await async_client.get(
        f"/medicoes-rop/relatorios/{relatorio.id}/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests: Delete endpoint (DELETE /medicoes-rop/relatorios/{id})
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_excluir_relatorio_success(
    mock_boto_client, async_client, db_session, admin_token
):
    """DELETE /relatorios/{id} soft-deletes the report and clears missions.

    Validates Requirements: 4.1, 4.3
    """
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    entities = await _seed_base_entities(db_session)
    relatorio, missoes = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.delete(
        f"/medicoes-rop/relatorios/{relatorio.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data

    # Verify report is now EXCLUIDO
    await db_session.refresh(relatorio)
    assert relatorio.status == "EXCLUIDO"

    # Verify missions have medicao_enviada_em cleared
    for missao in missoes:
        await db_session.refresh(missao)
        assert missao.medicao_enviada_em is None


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_excluir_relatorio_restores_mission_eligibility(
    mock_boto_client, async_client, db_session, admin_token
):
    """After deletion, missions become eligible again (medicao_enviada_em = NULL).

    Validates Requirements: 4.4
    """
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    entities = await _seed_base_entities(db_session)
    relatorio, missoes = await _create_relatorio_with_missoes(
        db_session, entities, num_missoes=2,
    )

    # Confirm missions are NOT eligible before delete (medicao_enviada_em is set)
    for missao in missoes:
        await db_session.refresh(missao)
        assert missao.medicao_enviada_em is not None

    # Delete the report
    response = await async_client.delete(
        f"/medicoes-rop/relatorios/{relatorio.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    # Verify missions are now eligible (medicao_enviada_em cleared)
    for missao in missoes:
        await db_session.refresh(missao)
        assert missao.medicao_enviada_em is None


@pytest.mark.asyncio
async def test_excluir_relatorio_already_deleted(
    async_client, db_session, admin_token
):
    """DELETE /relatorios/{id} on already-deleted report returns 422.

    Validates Requirements: 4.6
    """
    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(
        db_session, entities, status="EXCLUIDO",
        s3_key="MEDICAO/cliente/Medicao_already_del.pdf",
    )

    response = await async_client.delete(
        f"/medicoes-rop/relatorios/{relatorio.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_excluir_relatorio_not_found(async_client, db_session, admin_token):
    """DELETE /relatorios/{id} with invalid id returns 404.

    Validates Requirements: 4.5
    """
    await _seed_base_entities(db_session)

    response = await async_client.delete(
        "/medicoes-rop/relatorios/99999",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_excluir_relatorio_s3_failure_still_succeeds(
    mock_boto_client, async_client, db_session, admin_token
):
    """DELETE succeeds even if S3 delete_object fails (resilience).

    Validates Requirements: 4.7
    """
    mock_s3 = MagicMock()
    mock_s3.delete_object.side_effect = Exception("S3 unavailable")
    mock_boto_client.return_value = mock_s3

    entities = await _seed_base_entities(db_session)
    relatorio, missoes = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.delete(
        f"/medicoes-rop/relatorios/{relatorio.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # Should still succeed despite S3 failure
    assert response.status_code == 200

    await db_session.refresh(relatorio)
    assert relatorio.status == "EXCLUIDO"

    for missao in missoes:
        await db_session.refresh(missao)
        assert missao.medicao_enviada_em is None


# ---------------------------------------------------------------------------
# Tests: Send endpoint (POST /medicoes-rop/relatorios/{id}/enviar)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.SesEmailService")
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_enviar_relatorio_success(
    mock_boto_client, mock_ses_class, async_client, db_session, admin_token
):
    """POST /relatorios/{id}/enviar sends email and updates report metadata.

    Validates Requirements: 5.1, 5.6, 5.7
    """
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/email-url"
    mock_boto_client.return_value = mock_s3

    mock_ses_instance = MagicMock()
    mock_ses_class.return_value = mock_ses_instance

    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.post(
        f"/medicoes-rop/relatorios/{relatorio.id}/enviar",
        json={
            "emails": ["cliente@example.com", "outro@example.com"],
            "mensagem": "Segue o relatório de medição.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "mensagem" in data

    # Verify SES was called
    mock_ses_instance.send_relatorio_email.assert_called_once()

    # Verify report metadata updated
    await db_session.refresh(relatorio)
    assert relatorio.enviado_em is not None
    assert "cliente@example.com" in relatorio.enviado_para
    assert "outro@example.com" in relatorio.enviado_para


@pytest.mark.asyncio
async def test_enviar_relatorio_invalid_emails(
    async_client, db_session, admin_token
):
    """POST /relatorios/{id}/enviar with invalid emails returns 422.

    Validates Requirements: 5.10
    """
    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.post(
        f"/medicoes-rop/relatorios/{relatorio.id}/enviar",
        json={
            "emails": ["not-an-email", "also@bad"],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_enviar_relatorio_empty_emails_list(
    async_client, db_session, admin_token
):
    """POST /relatorios/{id}/enviar with empty emails returns 422.

    Validates Requirements: 5.8
    """
    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.post(
        f"/medicoes-rop/relatorios/{relatorio.id}/enviar",
        json={"emails": []},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_enviar_relatorio_not_found(async_client, db_session, admin_token):
    """POST /relatorios/{id}/enviar with invalid id returns 404.

    Validates Requirements: 5.9
    """
    await _seed_base_entities(db_session)

    response = await async_client.post(
        "/medicoes-rop/relatorios/99999/enviar",
        json={"emails": ["valid@example.com"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.SesEmailService")
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_enviar_relatorio_ses_failure_returns_502(
    mock_boto_client, mock_ses_class, async_client, db_session, admin_token
):
    """POST /relatorios/{id}/enviar returns 502 when SES fails.

    Validates Requirements: 5.11
    """
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/email-url"
    mock_boto_client.return_value = mock_s3

    mock_ses_instance = MagicMock()
    mock_ses_instance.send_relatorio_email.side_effect = Exception("SES unavailable")
    mock_ses_class.return_value = mock_ses_instance

    entities = await _seed_base_entities(db_session)
    relatorio, _ = await _create_relatorio_with_missoes(db_session, entities)

    response = await async_client.post(
        f"/medicoes-rop/relatorios/{relatorio.id}/enviar",
        json={"emails": ["valid@example.com"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 502


# ---------------------------------------------------------------------------
# Tests: Full flow (generate → list → download → send → delete → verify)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@patch("app.services.gestao_relatorios_medicao_service.SesEmailService")
@patch("app.services.gestao_relatorios_medicao_service.boto3.client")
async def test_full_flow_generate_list_download_send_delete(
    mock_boto_client, mock_ses_class, async_client, db_session, admin_token
):
    """Full integration flow: create report in DB → list → download → send → delete → verify missions.

    This test simulates the complete lifecycle of a report without calling the
    actual gerar-relatorio endpoint (which requires PDF generation). Instead,
    we insert directly in DB then test all gestão endpoints.

    Validates Requirements: 2.1, 3.1, 4.1, 5.1
    """
    # Setup mocks
    mock_s3 = MagicMock()
    mock_s3.generate_presigned_url.return_value = "https://s3.example.com/full-flow-url"
    mock_boto_client.return_value = mock_s3

    mock_ses_instance = MagicMock()
    mock_ses_class.return_value = mock_ses_instance

    # Step 1: Create base entities and report
    entities = await _seed_base_entities(db_session)
    relatorio, missoes = await _create_relatorio_with_missoes(
        db_session, entities, num_missoes=2,
        s3_key="MEDICAO/cliente/Medicao_fullflow.pdf",
    )

    # Step 2: LIST — verify the report appears
    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"cliente_id": entities["cliente"].id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    found = [item for item in data["items"] if item["id"] == relatorio.id]
    assert len(found) == 1
    assert found[0]["status"] == "ATIVO"
    assert found[0]["qtd_missoes"] == 2

    # Step 3: DOWNLOAD — get presigned URL
    response = await async_client.get(
        f"/medicoes-rop/relatorios/{relatorio.id}/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["download_url"] == "https://s3.example.com/full-flow-url"

    # Step 4: SEND — send email
    response = await async_client.post(
        f"/medicoes-rop/relatorios/{relatorio.id}/enviar",
        json={
            "emails": ["destinatario@example.com"],
            "mensagem": "Mensagem personalizada para o cliente.",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    mock_ses_instance.send_relatorio_email.assert_called_once()

    # Verify report updated with send info
    await db_session.refresh(relatorio)
    assert relatorio.enviado_em is not None
    assert relatorio.enviado_para == "destinatario@example.com"

    # Step 5: DELETE — soft delete the report
    response = await async_client.delete(
        f"/medicoes-rop/relatorios/{relatorio.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200

    # Step 6: VERIFY — report is now EXCLUIDO
    await db_session.refresh(relatorio)
    assert relatorio.status == "EXCLUIDO"

    # Step 7: VERIFY — missions are eligible again (medicao_enviada_em cleared)
    for missao in missoes:
        await db_session.refresh(missao)
        assert missao.medicao_enviada_em is None

    # Step 8: VERIFY — listing no longer shows the deleted report (default filter)
    response = await async_client.get(
        "/medicoes-rop/relatorios",
        params={"cliente_id": entities["cliente"].id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    found_after = [item for item in data["items"] if item["id"] == relatorio.id]
    assert len(found_after) == 0

    # Step 9: VERIFY — download of deleted report returns 404
    response = await async_client.get(
        f"/medicoes-rop/relatorios/{relatorio.id}/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404
