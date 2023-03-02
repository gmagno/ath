import io
from typing import Any

import boto3

from app.core.config import Settings, get_settings

settings: Settings = get_settings()


def s3_obj_url(host, port, bucket, filename) -> str:
    url: str = f"http://{host}:{port}/{bucket}/{filename}"
    return url


def s3_plot_url(filename) -> str:
    url: str = s3_obj_url(
        host=settings.S3_HOST,
        port=settings.S3_PORT,
        bucket=settings.S3_PLOTS_BUCKET_NAME,
        filename=filename,
    )
    return url


def s3_csv_url(filename) -> str:
    url: str = s3_obj_url(
        host=settings.S3_HOST,
        port=settings.S3_PORT,
        bucket=settings.S3_CSVS_BUCKET_NAME,
        filename=filename,
    )
    return url


def s3_upload_file_from_memory(data: bytes, file_name: str, bucket: str) -> None:
    s3_url: str = f"http://" f"{settings.S3_HOST}:{settings.S3_PORT}"
    s3 = boto3.resource(
        "s3",
        endpoint_url=s3_url,
        region_name=settings.S3_REGION,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )
    client: Any = s3.meta.client
    with io.BytesIO(data) as f:
        client.upload_fileobj(f, bucket, file_name)
