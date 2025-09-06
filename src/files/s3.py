from contextlib import asynccontextmanager

from aiobotocore.session import get_session

from src.config import settings
from src.files.exceptions import FileNotFound


@asynccontextmanager
async def get_s3_client():
    """Create an async S3 client for MinIO."""
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as client:
        yield client


async def upload_to_s3(file_content: bytes, s3_key: str) -> None:
    """Upload a file to S3."""
    async with get_s3_client() as client:
        await client.put_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
        )


async def download_from_s3(s3_key: str) -> bytes:
    """Download a file from S3."""
    try:
        async with get_s3_client() as client:
            response = await client.get_object(
                Bucket=settings.AWS_S3_BUCKET_NAME,
                Key=s3_key,
            )
            return await response["Body"].read()
    except client.exceptions.NoSuchKey:
        raise FileNotFound()


async def delete_from_s3(s3_key: str) -> None:
    """Delete a file from S3."""
    async with get_s3_client() as client:
        await client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=s3_key,
        )
