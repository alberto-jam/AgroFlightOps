"""Property test: Required field validation for Medição ROP endpoint.

Feature: medicao-rop, Property 2: Required field validation
**Validates: Requirements 2.5**

For any combination of filter inputs where at least one of `cliente_id`,
`data_inicial`, or `data_final` is missing, the system should reject the
request with a validation error identifying the missing fields.
"""

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

# All three required fields for the endpoint
REQUIRED_FIELDS = {
    "cliente_id": "1",
    "data_inicial": "2024-01-01",
    "data_final": "2024-12-31",
}


def _non_empty_subsets(items: list) -> st.SearchStrategy:
    """Generate non-empty subsets of items (fields to omit)."""
    return st.lists(
        st.sampled_from(items), min_size=1, max_size=len(items), unique=True
    )


@pytest.mark.asyncio
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(fields_to_omit=_non_empty_subsets(list(REQUIRED_FIELDS.keys())))
async def test_property_2_required_field_validation(
    fields_to_omit: list[str], async_client, admin_token
):
    """Property 2: Any request missing at least one required field should be rejected with 422.

    Feature: medicao-rop, Property 2: Required field validation
    **Validates: Requirements 2.5**
    """
    # Build query params with some required fields omitted
    params = {k: v for k, v in REQUIRED_FIELDS.items() if k not in fields_to_omit}

    response = await async_client.get(
        "/medicoes-rop",
        params=params,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # FastAPI returns 422 when required Query params are missing
    assert response.status_code == 422, (
        f"Expected 422 when omitting {fields_to_omit}, got {response.status_code}. "
        f"Params sent: {params}"
    )

    # Verify the response contains error details (either standard or custom format)
    body = response.json()
    assert "detail" in body or "errors" in body, (
        f"Expected 'detail' or 'errors' key in 422 response body when omitting {fields_to_omit}"
    )
