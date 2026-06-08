from datetime import date

from fastapi import APIRouter, Depends, Query

from src.application.deps import get_query_service
from src.application.schemas.companies import (
    CompanyCompareResponse,
    CompanyCurrentResponse,
    CompanyHistoryResponse,
    CompanyLatestResponse,
    CompanyVersionResponse,
)
from src.application.services.query_service import QueryService

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyCurrentResponse])
def list_companies(service: QueryService = Depends(get_query_service)):
    return service.list_current_companies()


@router.get("/compare", response_model=list[CompanyCompareResponse])
def compare_companies(
    company_ids: list[int] = Query(..., description="Company IDs to compare"),
    as_of_date: date = Query(..., description="As-of date (YYYY-MM-DD)"),
    service: QueryService = Depends(get_query_service),
):
    return service.compare_companies_as_of(company_ids=company_ids, as_of_date=as_of_date)


@router.get("/{company_id}", response_model=CompanyLatestResponse)
def get_company(company_id: int, service: QueryService = Depends(get_query_service)):
    return service.get_company_latest(company_id)


@router.get("/{company_id}/versions", response_model=list[CompanyVersionResponse])
def get_company_versions(
    company_id: int, service: QueryService = Depends(get_query_service)
):
    return service.get_company_versions(company_id)


@router.get("/{company_id}/history", response_model=list[CompanyHistoryResponse])
def get_company_history(
    company_id: int, service: QueryService = Depends(get_query_service)
):
    return service.get_company_history(company_id)
