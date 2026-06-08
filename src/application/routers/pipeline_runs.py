from fastapi import APIRouter, Depends

from src.application.deps import get_query_service
from src.application.schemas.pipeline import (
    PipelineRunQualityResponse,
    PipelineRunResponse,
)
from src.application.services.query_service import QueryService

router = APIRouter(prefix="/pipeline/runs", tags=["pipeline"])


@router.get("", response_model=list[PipelineRunResponse])
def list_pipeline_runs(service: QueryService = Depends(get_query_service)):
    return service.list_pipeline_runs()


@router.get("/{run_id}", response_model=PipelineRunResponse)
def get_pipeline_run(run_id: int, service: QueryService = Depends(get_query_service)):
    return service.get_pipeline_run(run_id)


@router.get("/{run_id}/quality", response_model=PipelineRunQualityResponse)
def get_pipeline_run_quality(
    run_id: int, service: QueryService = Depends(get_query_service)
):
    return service.get_pipeline_run_quality(run_id)
