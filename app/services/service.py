from typing import List, Optional

from pydantic import UUID4
from sqlmodel import Session

from app import schemas
from app.services import crud
from app.utils.utils import bytes_to_base64_encoded_string
from app.workers.document_converter import convert_document


def process_document(session: Session, data: bytes, filename: str, document_id: UUID4, normalize: bool) -> schemas.DocumentSchema:
    document_base64_encoded_string: str = bytes_to_base64_encoded_string(data)
    document = crud.add_document(session, document_id, filename)
    convert_document.send(document_id.hex, document_base64_encoded_string, normalize)
    return document


def get_document(session: Session, document_id: UUID4) -> Optional[schemas.DocumentSchema]:
    return crud.get_document(session, document_id)


def get_page(session: Session, document_id: UUID4, page_number: int) -> Optional[bytes]:
    return crud.get_page(session, document_id, page_number)


def add_pages_to_db(session: Session, document_id: UUID4, images: List[bytes]) -> None:
    crud.add_pages_and_update_document(session, document_id, images)


def get_documents(session: Session, ) -> List[schemas.DocumentSchema]:
    return crud.get_documents(session)


def delete_documents(session: Session, ) -> schemas.ItemsToDeleteSchema:
    return crud.delete_documents(session)


def delete_document(session: Session, document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    return crud.delete_document(session, document_id)


def delete_pages(session: Session, document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    return crud.delete_pages(session, document_id)
