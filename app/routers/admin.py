from typing import List

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlmodel import Session

from app import schemas
from app.config.db import get_session
from app.services import service

router = APIRouter()


@router.get(
    "/documents",
    tags=["Admin"],
    response_model=List[schemas.DocumentSchema],
    response_model_exclude=["n_pages"]
)
def get_documents(session: Session = Depends(get_session)):
    return service.get_documents(session)


@router.delete(
    "/documents",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema
)
def delete_documents(session: Session = Depends(get_session)):
    return service.delete_documents(session)


@router.delete(
    "/documents/{id:uuid}",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_document(id: UUID4, session: Session = Depends(get_session)):
    return service.delete_document(session, id)


@router.delete(
    "/documents/{id:uuid}/pages",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_pages(id: UUID4, session: Session = Depends(get_session)):
    return service.delete_pages(session, id)
