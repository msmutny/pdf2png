from typing import List

from fastapi import APIRouter
from pydantic import UUID4
from sqlmodel import Session, select

from app import models, schemas
from app.config.db import engine


router = APIRouter()

# TODO - move to services/crud


@router.get(
    "/documents",
    tags=["Admin"],
    response_model=List[schemas.DocumentSchema],
    response_model_exclude=["n_pages"]
)
def get_documents():
    with Session(engine) as session:
        documents_db = session.exec(
            select(models.Document)
        ).all()
        documents = [schemas.DocumentSchema(**d.dict()) for d in documents_db]
    return documents


@router.delete(
    "/documents",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema
)
def delete_documents():
    with Session(engine) as session:
        documents_deleted = session.query(models.Document).delete()
        pages_deleted = session.query(models.Page).delete()
        session.commit()
    return schemas.ItemsToDeleteSchema(documents_deleted=documents_deleted, pages_deleted=pages_deleted)


@router.delete(
    "/documents/{id:uuid}",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_document(id: UUID4):
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == id).delete()
        document = session.get(models.Document, id)
        session.delete(document)
        session.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)


@router.delete(
    "/documents/{id:uuid}/pages",
    tags=["Admin"],
    response_model=schemas.ItemsToDeleteSchema,
    response_model_exclude=["documents_deleted"]
)
def delete_pages(id: UUID4):
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == id).delete()
        session.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)