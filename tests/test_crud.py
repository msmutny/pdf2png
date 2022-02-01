from typing import List

from sqlmodel import Session

from app import schemas
from app.services import crud
from app.utils.utils import generate_uuid


# TODO - complete the CRUD tests


def test_get_documents_from_empty_database(session: Session):
    documents = crud.get_documents(session)
    assert len(documents) == 0


def test_add_document(session: Session):
    document_id = generate_uuid()
    filename = "foo.pdf"
    document: schemas.DocumentSchema = crud.add_document(session, document_id=document_id, filename=filename)
    assert document is not None
    assert document.status == 'processing'
    assert document.filename == filename
    assert document.id == document_id


def test_add_document_then_add_pages(session: Session):
    document_id = generate_uuid()
    filename = "foo.pdf"
    crud.add_document(session, document_id=document_id, filename=filename)
    n_pages = 10
    images_bytes: List[bytes] = [b"123"*i for i, _ in enumerate(range(n_pages))]
    crud.add_pages_and_update_document(session, document_id, images_bytes)
    document: schemas.DocumentSchema = crud.get_document(session, document_id)
    assert document is not None
    assert document.status == 'done'
    assert document.filename == filename
    assert document.id == document_id
    assert document.n_pages == n_pages

