"""Document uploads for verification (ID, registration certificate).

Local disk by default. The interface is deliberately small so it can be swapped
for S3/GCS without touching the routers.
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


class StorageError(Exception):
    pass


@dataclass(frozen=True)
class StoredFile:
    key: str
    url: str
    size: int
    content_type: str
    sha256: str


def _sniff(head: bytes) -> str | None:
    for magic, ctype in MAGIC.items():
        if head.startswith(magic):
            return ctype
    return None


def save_upload(upload: UploadFile, *, owner: str) -> StoredFile:
    """Validate by content (not by the client's claim) and store it."""
    data = upload.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            f"File larger than {settings.max_upload_bytes // (1024*1024)} MB")
    if not data:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Empty file")

    ctype = _sniff(data[:8])
    if ctype is None or ctype not in settings.allowed_types:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Only JPEG, PNG or PDF documents are accepted")

    ext = {"image/jpeg": "jpg", "image/png": "png", "application/pdf": "pdf"}[ctype]
    digest = hashlib.sha256(data).hexdigest()
    key = f"{owner}/{secrets.token_hex(8)}.{ext}"
    path = os.path.join(settings.upload_dir, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)
    return StoredFile(key=key, url=f"/uploads/{key}", size=len(data),
                      content_type=ctype, sha256=digest)
