"""Unit tests for access control on the GET /medicoes-rop endpoint.

Validates Requirements 7.1, 7.2, 7.3:
- ADMINISTRADOR and FINANCEIRO profiles can access the endpoint (HTTP 200 or 404/422, but NOT 401/403)
- Other profiles receive HTTP 403
- Requests without a token receive HTTP 401
"""

import pytest

# Valid query params to pass FastAPI validation (the endpoint requires these)
VALID_PARAMS = {
    "cliente_id": 1,
    "data_inicial": "2024-01-01",
    "data_final": "2024-12-31",
}


@pytest.mark.asyncio
async def test_admin_can_access_medicao_rop(async_client, admin_token):
    """ADMINISTRADOR should pass auth — expects anything except 401/403."""
    response = await async_client.get(
        "/medicoes-rop",
        params=VALID_PARAMS,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_financeiro_can_access_medicao_rop(async_client, financeiro_token):
    """FINANCEIRO should pass auth — expects anything except 401/403."""
    response = await async_client.get(
        "/medicoes-rop",
        params=VALID_PARAMS,
        headers={"Authorization": f"Bearer {financeiro_token}"},
    )
    assert response.status_code != 401
    assert response.status_code != 403


@pytest.mark.asyncio
async def test_piloto_cannot_access_medicao_rop(async_client, piloto_token):
    """PILOTO should be forbidden — expects HTTP 403."""
    response = await async_client.get(
        "/medicoes-rop",
        params=VALID_PARAMS,
        headers={"Authorization": f"Bearer {piloto_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_tecnico_cannot_access_medicao_rop(async_client, tecnico_token):
    """TECNICO should be forbidden — expects HTTP 403."""
    response = await async_client.get(
        "/medicoes-rop",
        params=VALID_PARAMS,
        headers={"Authorization": f"Bearer {tecnico_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_cannot_access_medicao_rop(async_client):
    """Request without Authorization header should get HTTP 401."""
    response = await async_client.get(
        "/medicoes-rop",
        params=VALID_PARAMS,
    )
    assert response.status_code == 401
