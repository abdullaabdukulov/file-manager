from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.auth.dependencies import get_current_user
from src.files.constants import Visibility
from src.files.schemas import FileResponse, FileUploadRequest
from src.files.service import (
    delete_file,
    download_file,
    get_file,
    list_files,
    upload_file,
)

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileResponse)
async def upload_file_endpoint(
    file: UploadFile = File(...),
    visibility: Visibility = Query(
        ..., description="Visibility: PRIVATE, DEPARTMENT, or PUBLIC"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Upload a file to S3 with visibility and role-based validation."""
    upload_request = FileUploadRequest(visibility=visibility)
    file_record = await upload_file(file, upload_request.visibility, current_user)
    return FileResponse(**file_record)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file_info(file_id: UUID, current_user: dict = Depends(get_current_user)):
    """Get file details and metadata with access checks."""
    file = await get_file(file_id, current_user)
    return FileResponse(**file)


@router.get("/{file_id}/download")
async def download_file_endpoint(
    file_id: UUID, current_user: dict = Depends(get_current_user)
):
    """Download a file from S3 with access checks."""
    file_content, filename = await download_file(file_id, current_user)
    return StreamingResponse(
        BytesIO(file_content),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: UUID, current_user: dict = Depends(get_current_user)
):
    """Delete a file from S3 and database with access checks."""
    await delete_file(file_id, current_user)
    return {"message": "File deleted"}


@router.get("/", response_model=list[FileResponse])
async def list_files_endpoint(
    department_id: UUID | None = Query(
        None, description="Optional department ID to filter files"
    ),
    current_user: dict = Depends(get_current_user),
):
    """List files accessible to the user, optionally filtered by department."""
    files = await list_files(department_id, current_user)
    return [FileResponse(**f) for f in files]
