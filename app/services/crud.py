import base64
import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from starlette import status
from pydantic import UUID4

from app import models, schemas
from app.config.db import engine

# TODO - remove HTTP related stuff


def add_document(document_id: UUID4) -> schemas.DocumentSchema:
    with Session(engine) as session:
        document = models.Document(id=document_id)
        session.add(document)
        session.commit()
        session.refresh(document)
        document_schema = schemas.DocumentSchema(**document.dict())
    return document_schema


def get_document(document_id: UUID4) -> schemas.DocumentSchema:
    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        n_pages: int = session.exec(
            select(func.count())
            .select_from(models.Page)
            .where(models.Page.document_id == document_id)
        ).first()
        document_schema = schemas.DocumentSchema(**document.dict())
        document_schema.n_pages = n_pages
    return document_schema


def get_page(document_id: UUID4, page_number: int) -> bytes:
    with Session(engine) as session:
        image_base64_encoded = session.exec(
            select(models.Page.image)
            .select_from(models.Page)
            .where(models.Page.document_id == document_id, models.Page.page_number == page_number)
        ).first()
        if not image_base64_encoded:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        image: bytes = base64.b64decode(image_base64_encoded)
    return image


def add_pages(document_id: UUID4, images: List[bytes]):
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


