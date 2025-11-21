from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional

import boto3
from botocore.client import Config

from .config import get_settings


def get_s3_client():
    settings = get_settings()
    session = boto3.session.Session()
    return session.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        use_ssl=settings.s3_use_ssl,
        config=Config(s3={"addressing_style": "path"}),
    )


def generate_presigned_put_url(key: str, content_type: Optional[str]) -> Dict[str, Any]:
    settings = get_settings()
    client = get_s3_client()
    params = {"Bucket": settings.s3_bucket, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    url = client.generate_presigned_url(
        "put_object",
        Params=params,
        ExpiresIn=settings.s3_presign_expire,
    )
    return {"url": url, "bucket": settings.s3_bucket, "key": key}


def generate_presigned_get_url(key: str) -> str:
    settings = get_settings()
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=settings.s3_presign_expire,
    )


def sha256_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
