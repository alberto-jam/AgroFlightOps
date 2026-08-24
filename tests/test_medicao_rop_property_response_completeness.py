"""Property test: Response completeness for Medição ROP.

Feature: medicao-rop, Property 6: Response completeness
**Validates: Requirements 4.1**

For any mission returned by the query, the response object must include all
required fields: `id`, `codigo`, `propriedade_nome`, `talhao_nome`,
`encerrado_tecnicamente_em`, `area_realizada`, and `status`.
"""

from datetime import datetime
from decimal import Decimal

from hypothesis import given, settings, strategies as st

from app.models.enums import MissaoStatus
from app.repositories.medicao_rop_repository import MedicaoRopMissaoRow
from app.schemas.medicao_rop import MedicaoRopMissaoResponse

# Strategies for generating random MedicaoRopMissaoRow fields
st_id = st.integers(min_value=1, max_value=2**31 - 1)
st_codigo = st.text(min_size=1, max_size=50, alphabet=st.characters(categories=("L", "N", "P")))
st_nome = st.text(min_size=1, max_size=100, alphabet=st.characters(categories=("L", "N", "S")))
st_datetime = st.datetimes(min_value=datetime(2000, 1, 1), max_value=datetime(2099, 12, 31))
st_area = st.one_of(
    st.none(),
    st.decimals(
        min_value=Decimal("0.01"),
        max_value=Decimal("99999.99"),
        places=2,
        allow_nan=False,
        allow_infinity=False,
    ),
)
st_status = st.sampled_from(list(MissaoStatus))


@settings(max_examples=100)
@given(
    id=st_id,
    codigo=st_codigo,
    propriedade_nome=st_nome,
    talhao_nome=st_nome,
    encerrado_tecnicamente_em=st_datetime,
    area_realizada=st_area,
    status=st_status,
)
def test_property_6_response_completeness(
    id: int,
    codigo: str,
    propriedade_nome: str,
    talhao_nome: str,
    encerrado_tecnicamente_em: datetime,
    area_realizada: Decimal | None,
    status: MissaoStatus,
):
    """Property 6: MedicaoRopMissaoResponse always includes all required fields.

    Feature: medicao-rop, Property 6: Response completeness
    **Validates: Requirements 4.1**
    """
    # Build a MedicaoRopMissaoRow with random data
    row = MedicaoRopMissaoRow(
        id=id,
        codigo=codigo,
        propriedade_nome=propriedade_nome,
        talhao_nome=talhao_nome,
        encerrado_tecnicamente_em=encerrado_tecnicamente_em,
        area_realizada=area_realizada,
        status=status.value,
    )

    # Validate using Pydantic's from_attributes (model_validate)
    response = MedicaoRopMissaoResponse.model_validate(row, from_attributes=True)

    # Assert all required fields are present and have correct types
    assert response.id == id
    assert isinstance(response.id, int)

    assert response.codigo == codigo
    assert isinstance(response.codigo, str)

    assert response.propriedade_nome == propriedade_nome
    assert isinstance(response.propriedade_nome, str)

    assert response.talhao_nome == talhao_nome
    assert isinstance(response.talhao_nome, str)

    assert response.encerrado_tecnicamente_em == encerrado_tecnicamente_em
    assert isinstance(response.encerrado_tecnicamente_em, datetime)

    assert response.area_realizada == area_realizada
    assert response.area_realizada is None or isinstance(response.area_realizada, Decimal)

    assert response.status == status
    assert isinstance(response.status, MissaoStatus)

    # Verify all required fields are present in serialized output
    response_dict = response.model_dump()
    required_fields = {
        "id", "codigo", "propriedade_nome", "talhao_nome",
        "encerrado_tecnicamente_em", "area_realizada", "status",
    }
    missing = required_fields - set(response_dict.keys())
    assert not missing, f"Missing fields in response: {missing}"
