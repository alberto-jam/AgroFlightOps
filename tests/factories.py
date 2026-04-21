"""Hypothesis strategies for generating valid entity data dicts."""

from datetime import date, time, timedelta
from decimal import Decimal

import hypothesis.strategies as st

from app.models.enums import (
    BateriaStatus,
    ChecklistStatusGeral,
    DocumentoEntidade,
    DocumentoStatus,
    DroneStatus,
    FinanceiroStatus,
    ItemChecklistStatus,
    MissaoStatus,
    OrdemServicoStatus,
    Prioridade,
    Severidade,
)

# ---------------------------------------------------------------------------
# Reusable building-block strategies
# ---------------------------------------------------------------------------
_short_text = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N")),
    min_size=1,
    max_size=40,
).filter(lambda s: s.strip() != "")

_optional_text = st.one_of(st.none(), _short_text)

_latitude = st.decimals(
    min_value=Decimal("-90"), max_value=Decimal("90"),
    places=7, allow_nan=False, allow_infinity=False,
)

_longitude = st.decimals(
    min_value=Decimal("-180"), max_value=Decimal("180"),
    places=7, allow_nan=False, allow_infinity=False,
)

_positive_decimal = st.decimals(
    min_value=Decimal("0"), max_value=Decimal("99999"),
    places=2, allow_nan=False, allow_infinity=False,
)

_positive_decimal_3 = st.decimals(
    min_value=Decimal("0"), max_value=Decimal("99999"),
    places=3, allow_nan=False, allow_infinity=False,
)

_estado = st.text(
    alphabet=st.characters(whitelist_categories=("Lu",)),
    min_size=2, max_size=2,
)

_simple_email = st.builds(
    lambda user, domain: f"{user}@{domain}.com",
    user=st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=3, max_size=15),
    domain=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=10),
)

_future_date = st.dates(min_value=date.today(), max_value=date(2030, 12, 31))
_past_date = st.dates(min_value=date(2020, 1, 1), max_value=date.today())
_any_date = st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))
_any_time = st.times()


# ---------------------------------------------------------------------------
# Entity strategies — each returns a dict matching the *Create schema
# ---------------------------------------------------------------------------


@st.composite
def perfil_strategy(draw):
    return {
        "nome": draw(_short_text.map(lambda s: s[:80])),
        "descricao": draw(_optional_text),
    }


@st.composite
def usuario_strategy(draw, perfil_id: int = 1):
    return {
        "nome": draw(_short_text.map(lambda s: s[:200])),
        "email": draw(
            _simple_email.map(lambda e: e[:255])
        ),
        "perfil_id": perfil_id,
        "senha": draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N")),
                min_size=6, max_size=30,
            )
        ),
    }


@st.composite
def cliente_strategy(draw):
    return {
        "nome": draw(_short_text.map(lambda s: s[:200])),
        "cpf_cnpj": draw(st.one_of(st.none(), st.text(min_size=11, max_size=18, alphabet="0123456789.-/"))),
        "telefone": draw(st.one_of(st.none(), st.text(min_size=8, max_size=15, alphabet="0123456789()-+ "))),
        "email": draw(st.one_of(st.none(), _simple_email.map(lambda e: e[:255]))),
        "endereco": draw(_optional_text),
        "numero": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20, alphabet="0123456789"))),
        "complemento": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "bairro": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "municipio": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "estado": draw(st.one_of(st.none(), _estado)),
        "cep": draw(st.one_of(st.none(), st.text(min_size=8, max_size=12, alphabet="0123456789-"))),
        "latitude": draw(st.one_of(st.none(), _latitude)),
        "longitude": draw(st.one_of(st.none(), _longitude)),
        "referencia_local": draw(_optional_text),
    }


@st.composite
def cultura_strategy(draw):
    return {
        "nome": draw(_short_text.map(lambda s: s[:120])),
        "descricao": draw(_optional_text),
    }


@st.composite
def propriedade_strategy(draw, cliente_id: int = 1):
    return {
        "cliente_id": cliente_id,
        "nome": draw(_short_text.map(lambda s: s[:200])),
        "endereco": draw(_optional_text),
        "numero": draw(st.one_of(st.none(), st.text(min_size=1, max_size=20, alphabet="0123456789"))),
        "complemento": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "bairro": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "municipio": draw(_short_text.map(lambda s: s[:120])),
        "estado": draw(_estado),
        "cep": draw(st.one_of(st.none(), st.text(min_size=8, max_size=12, alphabet="0123456789-"))),
        "localizacao_descritiva": draw(_optional_text),
        "referencia_local": draw(_optional_text),
        "latitude": draw(st.one_of(st.none(), _latitude)),
        "longitude": draw(st.one_of(st.none(), _longitude)),
        "area_total": draw(_positive_decimal),
    }


@st.composite
def talhao_strategy(draw, propriedade_id: int = 1, cultura_id: int = 1):
    return {
        "propriedade_id": propriedade_id,
        "nome": draw(_short_text.map(lambda s: s[:150])),
        "area_hectares": draw(_positive_decimal),
        "cultura_id": cultura_id,
        "observacoes": draw(_optional_text),
        "latitude": draw(st.one_of(st.none(), _latitude)),
        "longitude": draw(st.one_of(st.none(), _longitude)),
        "ponto_referencia": draw(_optional_text),
        "geojson": draw(st.one_of(st.none(), st.just({"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}))),
    }


@st.composite
def drone_strategy(draw):
    return {
        "identificacao": draw(_short_text.map(lambda s: s[:120])),
        "modelo": draw(_short_text.map(lambda s: s[:120])),
        "fabricante": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "capacidade_litros": draw(_positive_decimal),
        "status": draw(st.sampled_from(DroneStatus)).value,
    }


@st.composite
def bateria_strategy(draw, drone_id: int | None = None):
    return {
        "identificacao": draw(_short_text.map(lambda s: s[:120])),
        "drone_id": drone_id,
        "status": draw(st.sampled_from(BateriaStatus)).value,
        "observacoes": draw(_optional_text),
    }


@st.composite
def insumo_strategy(draw):
    return {
        "nome": draw(_short_text.map(lambda s: s[:200])),
        "fabricante": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:120]))),
        "unidade_medida": draw(st.sampled_from(["L", "mL", "kg", "g", "un"])),
        "saldo_atual": draw(_positive_decimal_3),
        "lote": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:100]))),
        "validade": draw(st.one_of(st.none(), _future_date.map(str))),
    }


@st.composite
def tipo_ocorrencia_strategy(draw):
    return {
        "nome": draw(_short_text.map(lambda s: s[:120])),
        "descricao": draw(_optional_text),
    }


@st.composite
def item_checklist_padrao_strategy(draw):
    return {
        "nome_item": draw(_short_text.map(lambda s: s[:200])),
        "descricao": draw(_optional_text),
        "obrigatorio": draw(st.booleans()),
        "ordem_exibicao": draw(st.integers(min_value=0, max_value=999)),
    }


@st.composite
def ordem_servico_strategy(
    draw,
    cliente_id: int = 1,
    propriedade_id: int = 1,
    talhao_id: int = 1,
    cultura_id: int = 1,
):
    return {
        "cliente_id": cliente_id,
        "propriedade_id": propriedade_id,
        "talhao_id": talhao_id,
        "cultura_id": cultura_id,
        "tipo_aplicacao": draw(_short_text.map(lambda s: s[:120])),
        "prioridade": draw(st.sampled_from(Prioridade)).value,
        "descricao": draw(_optional_text),
        "data_prevista": draw(_future_date.map(str)),
    }


@st.composite
def missao_strategy(
    draw,
    ordem_servico_id: int = 1,
    piloto_id: int = 1,
    drone_id: int = 1,
    tecnico_id: int | None = None,
):
    return {
        "ordem_servico_id": ordem_servico_id,
        "piloto_id": piloto_id,
        "tecnico_id": tecnico_id,
        "drone_id": drone_id,
        "data_agendada": draw(_future_date.map(str)),
        "hora_agendada": draw(_any_time.map(lambda t: t.isoformat())),
        "area_prevista": draw(_positive_decimal),
        "volume_previsto": draw(_positive_decimal_3),
        "janela_operacional": draw(_optional_text),
        "restricoes": draw(_optional_text),
        "observacoes_planejamento": draw(_optional_text),
        "latitude_operacao": draw(st.one_of(st.none(), _latitude)),
        "longitude_operacao": draw(st.one_of(st.none(), _longitude)),
        "endereco_operacao": draw(_optional_text),
        "referencia_operacao": draw(_optional_text),
    }


@st.composite
def checklist_missao_strategy(draw, missao_id: int = 1, preenchido_por: int = 1):
    return {
        "missao_id": missao_id,
        "status_geral": draw(st.sampled_from(ChecklistStatusGeral)).value,
        "preenchido_por": preenchido_por,
    }


@st.composite
def item_checklist_missao_strategy(draw, checklist_id: int = 1):
    return {
        "checklist_id": checklist_id,
        "nome_item": draw(_short_text.map(lambda s: s[:200])),
        "obrigatorio": draw(st.booleans()),
        "status_item": draw(st.sampled_from(ItemChecklistStatus)).value,
        "observacao": draw(_optional_text),
    }


@st.composite
def ocorrencia_strategy(
    draw, missao_id: int = 1, tipo_ocorrencia_id: int = 1
):
    return {
        "missao_id": missao_id,
        "tipo_ocorrencia_id": tipo_ocorrencia_id,
        "descricao": draw(_short_text),
        "severidade": draw(st.sampled_from(Severidade)).value,
    }


@st.composite
def evidencia_strategy(draw, missao_id: int = 1):
    return {
        "missao_id": missao_id,
        "nome_arquivo": draw(_short_text.map(lambda s: s[:200] + ".jpg")),
        "url_arquivo": draw(st.one_of(st.none(), st.just("https://s3.example.com/file.jpg"))),
        "tipo_arquivo": draw(st.one_of(st.none(), st.sampled_from(["image/jpeg", "image/png", "application/pdf"]))),
        "latitude": draw(st.one_of(st.none(), _latitude)),
        "longitude": draw(st.one_of(st.none(), _longitude)),
    }


@st.composite
def manutencao_strategy(draw, drone_id: int = 1):
    d = draw(_past_date)
    prox = draw(st.one_of(
        st.none(),
        st.dates(min_value=d, max_value=date(2030, 12, 31)).map(str),
    ))
    return {
        "drone_id": drone_id,
        "tipo": draw(_short_text.map(lambda s: s[:100])),
        "descricao": draw(_optional_text),
        "data_manutencao": str(d),
        "proxima_manutencao": prox,
        "horas_na_data": draw(st.one_of(st.none(), _positive_decimal)),
    }


@st.composite
def financeiro_missao_strategy(draw, missao_id: int = 1):
    return {
        "custo_estimado": draw(_positive_decimal),
        "custo_realizado": draw(_positive_decimal),
        "valor_faturado": draw(_positive_decimal),
        "status_financeiro": draw(st.sampled_from(FinanceiroStatus)).value,
        "observacoes": draw(_optional_text),
    }


@st.composite
def auditoria_strategy(draw, usuario_id: int = 1):
    return {
        "entidade": draw(st.sampled_from([
            "usuario", "cliente", "cultura", "drone", "bateria",
            "insumo", "propriedade", "talhao", "ordem_servico", "missao",
        ])),
        "entidade_id": draw(st.integers(min_value=1, max_value=10000)),
        "acao": draw(st.sampled_from(["CREATE", "UPDATE", "DELETE"])),
        "valor_anterior": draw(st.one_of(st.none(), st.just({"campo": "antigo"}))),
        "valor_novo": draw(st.one_of(st.none(), st.just({"campo": "novo"}))),
        "usuario_id": usuario_id,
    }


@st.composite
def documento_oficial_strategy(draw, entidade_id: int = 1):
    d_emissao = draw(_past_date)
    d_validade = draw(st.one_of(
        st.none(),
        st.dates(min_value=d_emissao, max_value=date(2030, 12, 31)).map(str),
    ))
    return {
        "entidade": draw(st.sampled_from(DocumentoEntidade)).value,
        "entidade_id": entidade_id,
        "tipo_documento": draw(_short_text.map(lambda s: s[:120])),
        "descricao": draw(st.one_of(st.none(), _short_text.map(lambda s: s[:255]))),
        "nome_arquivo": draw(_short_text.map(lambda s: s[:200] + ".pdf")),
        "content_type": draw(st.sampled_from(["application/pdf", "image/jpeg", "image/png"])),
        "s3_key": draw(_short_text.map(lambda s: f"docs/{s[:100]}.pdf")),
        "bucket_s3": draw(st.one_of(st.none(), st.just("agroflightops-docs-test"))),
        "data_emissao": str(d_emissao),
        "data_validade": d_validade,
    }


@st.composite
def reserva_insumo_strategy(draw, missao_id: int = 1, insumo_id: int = 1):
    return {
        "missao_id": missao_id,
        "insumo_id": insumo_id,
        "quantidade_prevista": draw(_positive_decimal_3),
        "unidade_medida": draw(st.sampled_from(["L", "mL", "kg", "g", "un"])),
        "justificativa_excesso": draw(_optional_text),
    }


@st.composite
def consumo_insumo_missao_strategy(draw, missao_id: int = 1, insumo_id: int = 1):
    return {
        "missao_id": missao_id,
        "insumo_id": insumo_id,
        "quantidade_realizada": draw(_positive_decimal_3),
        "unidade_medida": draw(st.sampled_from(["L", "mL", "kg", "g", "un"])),
        "observacoes": draw(_optional_text),
        "justificativa_excesso": draw(_optional_text),
    }
