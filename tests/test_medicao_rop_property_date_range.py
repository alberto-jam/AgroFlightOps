"""Property test: Date range validation for MedicaoRopService.

**Validates: Requirements 2.6**

Property 3: Date range validation
For any pair of dates where data_final < data_inicial, the system should reject
the request with a validation error indicating the period is invalid.
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import pytest
from hypothesis import given, settings, strategies as st

from app.core.exceptions import BusinessRuleViolationError
from app.services.medicao_rop_service import MedicaoRopService


# Strategy: generate a base date and a positive timedelta so that
# data_final is always strictly before data_inicial.
@st.composite
def invalid_date_range(draw):
    """Generate a pair (data_inicial, data_final) where data_final < data_inicial."""
    # Pick any date within a reasonable range
    base_date = draw(st.dates(min_value=date(2000, 1, 2), max_value=date(2100, 12, 31)))
    # Offset at least 1 day so data_final is strictly before data_inicial
    days_before = draw(st.integers(min_value=1, max_value=3650))
    data_inicial = base_date
    data_final = base_date - timedelta(days=days_before)
    return data_inicial, data_final


@settings(max_examples=100)
@given(dates=invalid_date_range())
@pytest.mark.asyncio
async def test_property_3_date_range_validation(dates):
    """Feature: medicao-rop, Property 3: Date range validation

    **Validates: Requirements 2.6**

    For any pair of dates where data_final < data_inicial, the service
    should raise BusinessRuleViolationError with a message containing
    'Período inválido'.
    """
    data_inicial, data_final = dates

    # The date validation happens before any DB query, so a mock session suffices
    mock_session = AsyncMock()
    service = MedicaoRopService(db=mock_session)

    with pytest.raises(BusinessRuleViolationError) as exc_info:
        await service.list_missoes_elegiveis(
            cliente_id=1,
            data_inicial=data_inicial,
            data_final=data_final,
            propriedade_id=None,
            page=1,
            page_size=20,
        )

    assert "Período inválido" in exc_info.value.message
