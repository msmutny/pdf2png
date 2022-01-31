import base64
import logging
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import Session, select
from pydantic import UUID4

from app import models, schemas


def add_document(db: Session, document_id: UUID4, filename: str) -> schemas.DocumentSchema:
    document = models.Document(id=document_id, filename=filename)
    db.add(document)
    db.commit()
    db.refresh(document)
    document_schema = schemas.DocumentSchema(**document.dict())
    return document_schema


def get_document(db: Session, document_id: UUID4) -> Optional[schemas.DocumentSchema]:
    document = db.get(models.Document, document_id)
    if not document:
        return None
    n_pages: int = db.exec(
        select(func.count())
        .select_from(models.Page)
        .where(models.Page.document_id == document_id)
    ).first()
    document_schema = schemas.DocumentSchema(**document.dict())
    document_schema.n_pages = n_pages
    return document_schema


def update_document_with_status(db: Session, document_id: UUID4, status: str) -> None:
    document = db.get(models.Document, document_id)
    document.status = status
    db.add(document)
    db.commit()


def get_page(db: Session, document_id: UUID4, page_number: int) -> Optional[bytes]:
    image_base64_encoded = db.exec(
        select(models.Page.image)
        .select_from(models.Page)
        .where(models.Page.document_id == document_id, models.Page.page_number == page_number)
    ).first()
    if not image_base64_encoded:
        return None
    image: bytes = base64.b64decode(image_base64_encoded)
    return image


def add_pages_and_update_document(db: Session, document_id: UUID4, images: List[bytes]) -> None:
    document = db.get(models.Document, document_id)
    if not document:
        logging.error(f"Cannot find document with ID {document_id} in the database!")
        return

    for page_num, image in enumerate(images, start=1):
        page = models.Page(image=base64.b64encode(image), page_number=page_num, document=document)
        db.add(page)

    document.status = 'done'
    db.add(document)
    db.commit()


def get_documents(db: Session) -> List[schemas.DocumentSchema]:
    documents_db = db.exec(
        select(models.Document)
    ).all()
    documents = [schemas.DocumentSchema(**d.dict()) for d in documents_db]
    return documents


def delete_documents(db: Session) -> schemas.ItemsToDeleteSchema:
    documents_deleted = db.query(models.Document).delete()
    pages_deleted = db.query(models.Page).delete()
    db.commit()
    return schemas.ItemsToDeleteSchema(documents_deleted=documents_deleted, pages_deleted=pages_deleted)


def delete_document(db: Session, document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    pages_deleted = db.query(models.Page).filter(models.Page.document_id == document_id).delete()
    document = db.get(models.Document, document_id)
    db.delete(document)
    db.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)


def delete_pages(db: Session, document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    pages_deleted = db.query(models.Page).filter(models.Page.document_id == document_id).delete()
    db.commit()
    return schemas.ItemsToDeleteSchema(pages_deleted=pages_deleted)

