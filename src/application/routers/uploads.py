from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from src.application.deps import get_query_service
from src.application.schemas.uploads import (
    UploadDetailsResponse,
    UploadResponse,
    UploadStatsResponse,
)
from src.application.services.query_service import QueryService

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.get("", response_model=list[UploadResponse])
def list_uploads(service: QueryService = Depends(get_query_service)):
    return service.list_uploads()


@router.get("/stats", response_model=list[UploadStatsResponse])
def get_upload_stats(service: QueryService = Depends(get_query_service)):
    return service.list_upload_stats()


@router.get("/{upload_id}/details", response_model=UploadDetailsResponse)
def get_upload_details(upload_id: int, service: QueryService = Depends(get_query_service)):
    return service.get_upload_details(upload_id)


@router.get("/{upload_id}/file")
def download_upload_file(upload_id: int, service: QueryService = Depends(get_query_service)):
    file_path = service.get_upload_file_path(upload_id)
    return FileResponse(path=file_path, filename=file_path.name)
