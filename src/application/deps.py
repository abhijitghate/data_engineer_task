from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.repositories.read_repository import ReadRepository
from src.application.services.query_service import QueryService
from src.database.database import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_query_service(db: Session = Depends(get_db_session)) -> QueryService:
    return QueryService(ReadRepository(db))
