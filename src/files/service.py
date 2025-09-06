import logging
import uuid
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy import select, update

from src.database import execute, fetch_all, fetch_one
from src.files.constants import FileType, Visibility
from src.files.exceptions import (
    FileAccessDenied,
    FileNotFound,
    FileSizeExceeded,
    InvalidFileType,
    InvalidVisibility,
)
from src.files.models import File, FileMetadata
from src.files.s3 import delete_from_s3, download_from_s3, upload_to_s3
from src.files.utils import get_file_type
from src.tasks import extract_metadata
from src.users.constants import Role

logger = logging.getLogger(__name__)


async def validate_file_upload(
    file: UploadFile, visibility: Visibility, current_user: dict
) -> tuple[str, FileType]:
    """Validate file size, type, and visibility based on user role."""
    role = Role(current_user["role"])
    file_type = get_file_type(file.filename)

    max_size_mb = {Role.USER: 10, Role.MANAGER: 50, Role.ADMIN: 100}
    max_size_bytes = max_size_mb[role] * 1024 * 1024
    file_size = file.size
    if file_size > max_size_bytes:
        raise FileSizeExceeded()

    if role == Role.USER and file_type != FileType.PDF:
        raise InvalidFileType(detail="Users can only upload PDF files")

    if role == Role.USER and visibility != Visibility.PRIVATE:
        raise InvalidVisibility(detail="Users can only upload private files")

    return file.filename, file_type


async def upload_file(
    file: UploadFile, visibility: Visibility, current_user: dict
) -> dict:
    """Upload a file to S3, save metadata, and trigger metadata extraction."""
    filename, file_type = await validate_file_upload(file, visibility, current_user)
    s3_key = f"files/{current_user['id']}/{uuid.uuid4().hex}/{filename}"
    file_content = await file.read()  # Read the entire file content
    await upload_to_s3(file_content, s3_key)

    file_data = {
        "owner_id": current_user["id"],
        "department_id": current_user["department_id"],
        "filename": filename,
        "file_type": file_type,
        "visibility": visibility,
        "file_size": len(file_content),
        "s3_key": s3_key,
    }
    insert_query = File.__table__.insert().values(**file_data)
    await execute(insert_query, commit_after=True)

    file_record = await fetch_one(select(File).where(File.s3_key == s3_key))
    logger.info(f"File uploaded: {file_record['id']}, triggering metadata extraction")
    extract_metadata.delay(str(file_record["id"]), s3_key, file_type.value)
    return file_record


async def get_file(file_id: UUID, current_user: dict) -> dict:
    """Get file details with access checks."""
    file = await fetch_one(select(File).where(File.id == file_id))
    if not file:
        raise FileNotFound()

    if await can_access_file(file, current_user):
        file_metadata = await fetch_one(
            select(FileMetadata).where(FileMetadata.file_id == file_id)
        )
        file["file_metadata"] = file_metadata if file_metadata else {}
        return file
    raise FileAccessDenied()


async def download_file(file_id: UUID, current_user: dict) -> tuple[bytes, str]:
    """Download a file from S3 with access checks."""
    file = await fetch_one(select(File).where(File.id == file_id))
    if not file:
        raise FileNotFound()

    if await can_access_file(file, current_user):
        file_content = await download_from_s3(file["s3_key"])
        await execute(
            update(File)
            .where(File.id == file_id)
            .values(download_count=File.download_count + 1),
            commit_after=True,
        )
        logger.info(
            f"File downloaded: {file_id}, \
            new download count: {file['download_count'] + 1}"
        )
        return file_content, file["filename"]
    raise FileAccessDenied()


async def delete_file(file_id: UUID, current_user: dict) -> None:
    """Delete a file from S3 and database with access checks."""
    file = await fetch_one(select(File).where(File.id == file_id))
    if not file:
        raise FileNotFound()

    role = Role(current_user["role"])
    if role == Role.USER and file["owner_id"] != current_user["id"]:
        raise FileAccessDenied(detail="Users can only delete their own files")

    if (
        role == Role.MANAGER
        and str(file["department_id"]) != current_user["department_id"]
    ):
        raise FileAccessDenied(
            detail="Managers can only delete files in their department"
        )

    await delete_from_s3(file["s3_key"])
    await execute(File.__table__.delete().where(File.id == file_id), commit_after=True)
    await execute(
        FileMetadata.__table__.delete().where(FileMetadata.file_id == file_id),
        commit_after=True,
    )
    logger.info(f"File deleted: {file_id}")


async def list_files(department_id: UUID | None, current_user: dict) -> list[dict]:
    """List files accessible to the user."""
    role = Role(current_user["role"])
    query = select(File)

    if role == Role.ADMIN:
        if department_id:
            query = query.where(File.department_id == department_id)
    elif role == Role.MANAGER:
        query = query.where(
            (File.visibility == Visibility.PUBLIC)
            | (File.department_id == current_user["department_id"])
            | (File.visibility == Visibility.DEPARTMENT)
        )
        if department_id:
            query = query.where(File.department_id == department_id)
    else:  # USER
        query = query.where(
            (File.visibility == Visibility.PUBLIC)
            | (
                File.department_id
                == current_user["department_id"] & File.visibility
                == Visibility.DEPARTMENT
            )
            | (File.owner_id == current_user["id"])
        )
        if department_id and department_id != current_user["department_id"]:
            raise FileAccessDenied(detail="Users cannot access other departments")

    files = await fetch_all(query)
    for file in files:
        file_metadata = await fetch_one(
            select(FileMetadata).where(FileMetadata.file_id == file["id"])
        )
        file["file_metadata"] = file_metadata if file_metadata else {}
    logger.info(f"Listed {len(files)} files for user {current_user['id']}")
    return files


async def can_access_file(file: dict, current_user: dict) -> bool:
    """Check if a user can access a file based on visibility and role."""
    role = Role(current_user["role"])
    if role == Role.ADMIN:
        return True
    if file["visibility"] == Visibility.PUBLIC:
        return True
    if file["visibility"] == Visibility.DEPARTMENT:
        return (
            role == Role.MANAGER
            or file["department_id"] == current_user["department_id"]
        )
    if file["visibility"] == Visibility.PRIVATE:
        return file["owner_id"] == current_user["id"]  # Direct UUID comparison
    return False
