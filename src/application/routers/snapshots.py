from datetime import date

from fastapi import APIRouter, Depends

from src.application.deps import get_query_service
from src.application.schemas.snapshots import SnapshotResponse
from src.application.services.query_service import QueryService

router = APIRouter(prefix="/snapshots", tags=["snapshots"])


@router.get("", response_model=list[SnapshotResponse])
def list_snapshots(
    service: QueryService = Depends(get_query_service),
    company_id: int | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    sector: str | None = None,
    country: str | None = None,
    currency: str | None = None,
):
    return service.list_snapshots(
        company_id=company_id,
        from_date=from_date,
        to_date=to_date,
        sector=sector,
        country=country,
        currency=currency,
    )


@router.get("/latest", response_model=list[SnapshotResponse])
def get_latest_snapshots(service: QueryService = Depends(get_query_service)):
    return service.get_latest_snapshots()


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
def get_snapshot(snapshot_id: int, service: QueryService = Depends(get_query_service)):
    return service.get_snapshot(snapshot_id)
