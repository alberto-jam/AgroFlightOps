"""Property test: Client-property association for MedicaoRopService.

**Validates: Requirements 2.2**

Property 1: Client-property association
For any client ID, when a propriedade_id is provided that does NOT belong to the
given cliente_id, the service should raise BusinessRuleViolationError.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings, strategies as st

from app.core.exceptions import BusinessRuleViolationError
from app.services.medicao_rop_service import MedicaoRopService


@st.composite
def mismatched_client_property(draw):
    """Generate two distinct client IDs and a property ID.

    The property will belong to owner_client_id, but the request
    will be made with requesting_client_id (always different).
    """
    requesting_client_id = draw(st.integers(min_value=1, max_value=10_000))
    # Ensure owner is always different from requesting client
    owner_client_id = draw(
        st.integers(min_value=1, max_value=10_000).filter(
            lambda x: x != requesting_client_id
        )
    )
    propriedade_id = draw(st.integers(min_value=1, max_value=10_000))
    return requesting_client_id, owner_client_id, propriedade_id


@settings(max_examples=100)
@given(data=mismatched_client_property())
@pytest.mark.asyncio
async def test_property_1_client_property_association(data):
    """Feature: medicao-rop, Property 1: Client-property association

    **Validates: Requirements 2.2**

    For any propriedade_id that does NOT belong to the given cliente_id,
    the service should raise BusinessRuleViolationError with a message
    containing 'não pertence ao cliente'.
    """
    requesting_client_id, owner_client_id, propriedade_id = data

    mock_session = AsyncMock()

    # Mock db.get: first call returns a Cliente (exists), second returns a Propriedade
    # owned by a different client
    mock_cliente = MagicMock()
    mock_cliente.id = requesting_client_id

    mock_propriedade = MagicMock()
    mock_propriedade.id = propriedade_id
    mock_propriedade.cliente_id = owner_client_id  # Different from requesting_client_id

    mock_session.get = AsyncMock(side_effect=[mock_cliente, mock_propriedade])

    service = MedicaoRopService(db=mock_session)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await service.list_missoes_elegiveis(
            cliente_id=requesting_client_id,
            data_inicial=date(2024, 1, 1),
            data_final=date(2024, 12, 31),
            propriedade_id=propriedade_id,
            page=1,
            page_size=20,
        )

    assert "não pertence ao cliente" in exc_info.value.message
