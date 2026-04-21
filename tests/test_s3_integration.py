"""S3 integration tests — upload, download, presigned URLs using moto mock.

Validates: Requirements 15.1, 15.7
"""

import io
import re

import boto3
import pytest
from moto import mock_aws

from app.core.config import settings


@pytest.fixture()
def s3_mock():
    """Start moto mock and create the test bucket."""
    with mock_aws():
        client = boto3.client("s3", region_name=settings.S3_REGION)
        client.create_bucket(Bucket=settings.S3_BUCKET)
        yield client


# ---------------------------------------------------------------------------
# Test: Upload stores file in S3 and metadata in DB (Req 15.1)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_documento_stores_in_s3(async_client, admin_token, s3_mock):
    """Upload via API should store file content in mock S3 and metadata in DB."""
    file_content = b"PDF content for testing upload"
    file_name = "registro_anac.pdf"

    resp = await async_client.post(
        "/documentos-oficiais",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "entidade": "DRONE",
            "entidade_id": "1",
            "tipo_documento": "REGISTRO_ANAC",
        },
        files={"file": (file_name, io.BytesIO(file_content), "application/pdf")},
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()

    # Verify DB metadata
    assert body["s3_key"].startswith("documentos-oficiais/DRONE/1/")
    assert body["s3_key"].endswith(".pdf")
    assert body["content_type"] == "application/pdf"
    assert body["nome_arquivo"] == file_name
    assert body["bucket_s3"] == settings.S3_BUCKET
    assert body["status"] == "ATIVO"
    assert body["entidade"] == "DRONE"
    assert body["entidade_id"] == 1

    # Verify S3 key pattern: documentos-oficiais/{entidade}/{entidade_id}/{uuid}.{ext}
    pattern = r"^documentos-oficiais/DRONE/1/[a-f0-9]+\.pdf$"
    assert re.match(pattern, body["s3_key"]), f"S3 key doesn't match pattern: {body['s3_key']}"

    # Verify file content in mock S3
    s3_obj = s3_mock.get_object(Bucket=settings.S3_BUCKET, Key=body["s3_key"])
    stored_content = s3_obj["Body"].read()
    assert stored_content == file_content


# ---------------------------------------------------------------------------
# Test: Download returns presigned URL (Req 15.7)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_download_returns_presigned_url(async_client, admin_token, s3_mock):
    """GET /documentos-oficiais/{id}/download should return a presigned URL."""
    file_content = b"Presigned URL test content"

    # Upload first
    upload_resp = await async_client.post(
        "/documentos-oficiais",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "entidade": "USUARIO",
            "entidade_id": "1",
            "tipo_documento": "LICENCA_PILOTO",
        },
        files={"file": ("licenca.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["id"]
    s3_key = upload_resp.json()["s3_key"]

    # Request download URL
    dl_resp = await async_client.get(
        f"/documentos-oficiais/{doc_id}/download",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert dl_resp.status_code == 200
    dl_body = dl_resp.json()

    # Verify presigned URL structure
    assert "url" in dl_body
    assert dl_body["expires_in"] == settings.S3_PRESIGNED_URL_EXPIRATION
    # URL should reference the correct bucket and key
    assert settings.S3_BUCKET in dl_body["url"]
    assert s3_key.replace("/", "%2F") in dl_body["url"] or s3_key in dl_body["url"]


# ---------------------------------------------------------------------------
# Test: Substitution marks previous document as SUBSTITUIDO (Req 15.5)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_upload_substitution_marks_previous_as_substituido(
    async_client, admin_token, s3_mock
):
    """Uploading a new doc with same tipo/entidade should mark previous as SUBSTITUIDO."""
    # Upload first document
    resp1 = await async_client.post(
        "/documentos-oficiais",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "entidade": "DRONE",
            "entidade_id": "10",
            "tipo_documento": "CERTIFICADO_ANAC",
        },
        files={"file": ("cert_v1.pdf", io.BytesIO(b"version 1"), "application/pdf")},
    )
    assert resp1.status_code == 201
    doc1_id = resp1.json()["id"]
    assert resp1.json()["status"] == "ATIVO"

    # Upload second document with same tipo/entidade
    resp2 = await async_client.post(
        "/documentos-oficiais",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "entidade": "DRONE",
            "entidade_id": "10",
            "tipo_documento": "CERTIFICADO_ANAC",
        },
        files={"file": ("cert_v2.pdf", io.BytesIO(b"version 2"), "application/pdf")},
    )
    assert resp2.status_code == 201
    assert resp2.json()["status"] == "ATIVO"

    # Verify first document is now SUBSTITUIDO
    get_resp = await async_client.get(
        f"/documentos-oficiais/{doc1_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["status"] == "SUBSTITUIDO"


# ---------------------------------------------------------------------------
# Test: Uploaded file content can be retrieved from mock S3
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_uploaded_file_content_retrievable_from_s3(
    async_client, admin_token, s3_mock
):
    """File content uploaded via API should be retrievable from mock S3."""
    file_content = b"Binary content \x00\x01\x02 for retrieval test"

    resp = await async_client.post(
        "/documentos-oficiais",
        headers={"Authorization": f"Bearer {admin_token}"},
        data={
            "entidade": "CLIENTE",
            "entidade_id": "5",
            "tipo_documento": "CONTRATO",
            "descricao": "Contrato de servico",
        },
        files={"file": ("contrato.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert resp.status_code == 201
    s3_key = resp.json()["s3_key"]

    # Retrieve from S3 and verify content matches
    s3_obj = s3_mock.get_object(Bucket=settings.S3_BUCKET, Key=s3_key)
    retrieved = s3_obj["Body"].read()
    assert retrieved == file_content
    assert s3_obj["ContentType"] == "application/pdf"
