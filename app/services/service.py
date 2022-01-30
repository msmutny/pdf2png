from typing import List

from pydantic import UUID4

from app import schemas
from app.services import crud
from app.utils.utils import bytes_to_base64_encoded_string
from app.workers.document_converter import convert_document

# TODO - remove HTTP related stuff


def process_document(data: bytes, filename: str, document_id: UUID4, normalize: bool) -> schemas.DocumentSchema:
    document_base64_encoded_string: str = bytes_to_base64_encoded_string(data)
    document = crud.add_document(document_id, filename)
    convert_document.send(str(document_id), document_base64_encoded_string, normalize)
    return document


def get_document(document_id: UUID4) -> schemas.DocumentSchema:
    return crud.get_document(document_id)


def get_page(document_id: UUID4, page_number: int) -> bytes:
    return crud.get_page(document_id, page_number)


def add_pages_to_db(document_id: UUID4, images: List[bytes]) -> None:
    crud.add_pages(document_id, images)


def get_documents() -> List[schemas.DocumentSchema]:
    return crud.get_documents()


def delete_documents() -> schemas.ItemsToDeleteSchema:
    return crud.delete_documents()


def delete_document(document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    return crud.delete_document(document_id)


def delete_pages(document_id: UUID4) -> schemas.ItemsToDeleteSchema:
    return crud.delete_pages(document_id)
