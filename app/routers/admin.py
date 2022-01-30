from typing import List

from fastapi import APIRouter
from pydantic import UUID4

from app import schemas
from app.services import service

router = APIRouter()


@router.get(
    "/documents",
    tags=["Admin"],
    response_model=List[schemas.DocumentSchema],
    response_model_exclude=["n_pages"]
)
def get_documents():
    return service.get_documents()


@router.delete(
    "/documents",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema
)
def delete_documents():
    return service.delete_documents()


@router.delete(
    "/documents/{id:uuid}",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_document(id: UUID4):
    return service.delete_document(id)


@router.delete(
    "/documents/{id:uuid}/pages",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_pages(id: UUID4):
    return service.delete_pages(id)
