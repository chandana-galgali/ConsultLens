"""Optional persistent S3-compatible storage for processed documents.

Credentials come from IAM or environment configuration, never source code.
"""
from pathlib import Path
from urllib.parse import urlparse
import logging
import uuid

from ..config import settings

logger = logging.getLogger(__name__)


def is_remote(path: str) -> bool:
    return path.startswith("s3://")


def store_processed_file(local_path: str) -> str:
    """Upload an already processed local file, returning durable identifier."""
    if not settings.s3_bucket:
        return local_path
    import boto3
    key = f"consultlens/{uuid.uuid4().hex}{Path(local_path).suffix.lower()}"
    client = boto3.client("s3", region_name=settings.aws_region,
                          endpoint_url=settings.s3_endpoint_url or None)
    client.upload_file(local_path, settings.s3_bucket, key)
    logger.info("document_stored", extra={"storage_provider": "s3"})
    return f"s3://{settings.s3_bucket}/{key}"


def get_remote_file(path: str):
    if not is_remote(path):
        raise ValueError("Expected remote storage identifier")
    import boto3
    uri = urlparse(path)
    client = boto3.client("s3", region_name=settings.aws_region,
                          endpoint_url=settings.s3_endpoint_url or None)
    response = client.get_object(Bucket=uri.netloc, Key=uri.path.lstrip("/"))
    return response["Body"]


def delete_file(path: str) -> None:
    if is_remote(path):
        import boto3
        uri = urlparse(path)
        client = boto3.client("s3", region_name=settings.aws_region,
                              endpoint_url=settings.s3_endpoint_url or None)
        client.delete_object(Bucket=uri.netloc, Key=uri.path.lstrip("/"))
    else:
        Path(path).unlink(missing_ok=True)
