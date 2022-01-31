import base64
import logging
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import Session, select
from pydantic import UUID4

from app import models, schemas
from app.config.db import engine


def add_document(document_id: UUID4, filename: str) -> schemas.DocumentSchema:
    with Session(engine) as session:
        document = models.Document(id=document_id, filename=filename)
        session.add(document)
        session.commit()
        session.refresh(document)
        document_schema = schemas.DocumentSchema(**document.dict())
    return document_schema


def get_document(document_id: UUID4) -> Optional[schemas.DocumentSchema]:
    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        if not document:
            return None
        n_pages: int = session.exec(
            select(func.count())
            .select_from(models.Page)
            .where(models.Page.document_id == document_id)
        ).first()
        document_schema = schemas.DocumentSchema(**document.dict())
        document_schema.n_pages = n_pages
    return document_schema


def update_document_with_status(document_id: UUID4, status: str) -> None:
    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        document.status = status
        session.add(document)
        session.commit()


def get_page(document_id: UUID4, page_number: int) -> Optional[bytes]:
    with Session(engine) as session:
        image_base64_encoded = session.exec(
            select(models.Page.image)
            .select_from(models.Page)
            .where(models.Page.document_id == document_id, models.Page.page_number == page_number)
        ).first()
        if not image_base64_encoded:
            return None
        image: bytes = base64.b64decode(image_base64_encoded)
    return image


def add_pages_and_update_document(document_id: UUID4, images: List[bytes]) -> None:
    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        if not document:
            logging.error(f"Cannot find document with ID {document_id} in the database!")
            return

        for page_num, image in enumerate(images, start=1):
            page = models.Page(image=base64.b64encode(image), page_number=page_num, document=document)
            session.add(page)

        document.status = 'done'
        session.add(document)
        session.commit()


def get_documents() -> List[schemas.DocumentSchema]:
    with Session(engine) as session:
        documents_db = session.exec(
            select(models.Document)
        ).all()
        documents = [schemas.DocumentSchema(**d.dict()) for d in documents_db]
    return documents


def delete_documents() -> schemas.ItemsToDeleteSchema:
    with Session(engine) as session:
        documents_deleted = session.query(models.Document).delete()
        pages_deleted = session.query(models.Page).delete()
        session.commit()
    return schemas.ItemsToDeleteSchema(documents_deleted=documents_deleted, pages_deleted=pages_deleted)


def delete_document(document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == document_id).delete()
        document = session.get(models.Document, document_id)
        session.delete(document)
        session.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)


def delete_pages(document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    with Session(engine) as session:
        pages_deleted = session.query(models.Page).filter(models.Page.document_id == document_id).delete()
        session.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)

