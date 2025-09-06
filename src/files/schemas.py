from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from src.files.constants import FileType, Visibility
from src.schemas import CustomModel


class FileUploadRequest(CustomModel):
    visibility: Visibility = Field(
        ..., description="Visibility level: PRIVATE, DEPARTMENT, or PUBLIC"
    )


class FileResponse(CustomModel):
    id: UUID
    owner_id: UUID
    department_id: UUID
    filename: str
    file_type: FileType
    visibility: Visibility
    file_size: int
    s3_key: str
    download_count: int
    created_at: datetime
    updated_at: datetime
    file_metadata: Optional[dict] = None
