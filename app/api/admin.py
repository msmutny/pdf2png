from typing import List

from fastapi import APIRouter
from pydantic import UUID4
from sqlmodel import Session, select

from app import models
from app.db import engine


router = APIRouter()


@router.get(
    "/documents",
    tags=["Admin"],
    response_model=List[models.Document],
    response_model_exclude=["n_pages"]
)
def get_documents():
    with Session(engine) as session:
        documents = session.exec(
            select(models.Document)
        )
        return documents.all()


@router.delete(
    "/documents",
    tags=["Admin"]
)
def delete_documents():
    with Session(engine) as session:
        documents_deleted = session.query(models.Document).delete()
        pages_deleted = session.query(models.Page).delete()
        session.commit()
    return {
        "documents_deleted": documents_deleted,
        "pages_deleted": pages_deleted
    }


@router.delete(
    "/documents/{id:uuid}",
    tags=["Admin"]
)
def delete_document(id: UUID4):
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == id).delete()
        document = session.get(models.Document, id)
        session.delete(document)
        session.commit()
    return {
        "pages_deleted": pages_deleted
    }


@router.delete(
    "/documents/{id:uuid}/pages",
    tags=["Admin"]
)
def delete_pages(id: UUID4):
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == id).delete()
        session.commit()
    return {
        "pages_deleted": pages_deleted
    }