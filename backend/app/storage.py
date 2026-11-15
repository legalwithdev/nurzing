"""Document storage.

Local disk by default; S3 when `NURZING_STORAGE=s3` and credentials are present.
Validation happens before anything is written, and it is based on the file's
actual bytes, never on the MIME type the client claims.
"""
from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass

from fastapi import HTTPException, UploadFile, status

from .config import settings

MAGIC = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"%PDF-": "application/pdf",
}
EXT = {"image/jpeg": "jpg", "image/png": "png", "application/pdf": "pdf"}


@dataclass(frozen=True)
class StoredFile:
    key: str
    url: str
    size: int
    content_type: str
    sha256: str
    backend: str


def sniff(head: bytes) -> str | None:
    for magic, ctype in MAGIC.items():
        if head.startswith(magic):
            return ctype
    return None


class LocalBackend:
    name = "local"

    def put(self, key: str, data: bytes) -> str:
        path = os.path.join(settings.upload_dir, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)
        return f"/uploads/{key}"


class S3Backend:
    name = "s3"

    def __init__(self) -> None:
        import boto3  # optional dependency
        self.bucket = settings.s3_bucket
        if not self.bucket:
            raise RuntimeError("NURZING_S3_BUCKET is not set")
        self.client = boto3.client(
            "s3",
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint or None,
            aws_access_key_id=settings.s3_access_key or None,
            aws_secret_access_key=settings.s3_secret_key or None,
        )

    def put(self, key: str, data: bytes) -> str:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data)
        if settings.s3_public_base:
            return f"{settings.s3_public_base.rstrip('/')}/{key}"
        return f"s3://{self.bucket}/{key}"


_BACKEND = None


def get_backend():
    global _BACKEND
    if _BACKEND is not None:
        return _BACKEND
    if settings.storage_backend == "s3":
        try:
            _BACKEND = S3Backend()
            return _BACKEND
        except Exception:
            # fall back rather than lose the upload
            pass
    _BACKEND = LocalBackend()
    return _BACKEND


def save_upload(upload: UploadFile, *, owner: str) -> StoredFile:
    data = upload.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            f"File larger than {settings.max_upload_bytes // (1024 * 1024)} MB")
    if not data:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Empty file")

    ctype = sniff(data[:8])
    if ctype is None or ctype not in settings.allowed_types:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Only JPEG, PNG or PDF documents are accepted")

    key = f"{owner}/{secrets.token_hex(8)}.{EXT[ctype]}"
    backend = get_backend()
    url = backend.put(key, data)
    return StoredFile(key=key, url=url, size=len(data), content_type=ctype,
                      sha256=hashlib.sha256(data).hexdigest(), backend=backend.name)
