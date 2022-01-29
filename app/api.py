import io
import base64
from typing import List
import warnings

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from pydantic import UUID4
from sqlmodel import Session, select
from starlette.responses import StreamingResponse
from pdf2image import convert_from_bytes
from sqlalchemy import func

from app import models
from app.settings import settings
from app.db import create_db_and_tables, engine
from app.utils import generate_uuid
from app.worker import convert_document

tags_metadata = [{"name": "Public"}, {"name": "Admin"}]
app = FastAPI(openapi_tags=tags_metadata)

# Temporary workaround for #https://github.com/tiangolo/sqlmodel/issues/189
warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


################
#  PUBLIC API  #
################
@app.post(
    "/documents",
    tags=["Public"],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=models.DocumentSchema,
    response_model_include=["id"]
)
def create_document(pdf: UploadFile = File(...)):
    content: bytes = pdf.file.read()
    content_base64_encoded_bytes: bytes = base64.b64encode(content)
    document_base64_encoded_string: str = content_base64_encoded_bytes.decode('ascii')

    uuid = generate_uuid()
    with Session(engine) as session:
        document = models.Document(id=uuid)
        session.add(document)
        session.commit()
        session.refresh(document)
        document_schema = models.DocumentSchema(**document.dict())

    convert_document.send(str(uuid), document_base64_encoded_string)

    return document_schema


@app.get(
    "/documents/{id:uuid}",
    tags=["Public"],
    response_model=models.DocumentSchema,
    response_model_include=["status", "n_pages"]
)
def get_document(id: UUID4):
    with Session(engine) as session:
        document = session.get(models.Document, id)
        if not document:
           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        n_pages: int = session.exec(
            select(func.count())
            .select_from(models.Page)
            .where(models.Page.document_id == id)
        ).first()
        document_schema = models.DocumentSchema(**document.dict())
        document_schema.n_pages = n_pages
    return document_schema


@app.get(
    "/documents/{id:uuid}/pages/{page_number:int}",
    tags=["Public"],
)
def get_page(id: UUID4, page_number: int):
    with Session(engine) as session:
        image_base64_encoded = session.exec(
            select(models.Page.image)
            .select_from(models.Page)
            .where(models.Page.document_id == id, models.Page.page_number == page_number)
        ).first()
        if not image_base64_encoded:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        image: bytes = base64.b64decode(image_base64_encoded)
    return StreamingResponse(io.BytesIO(image), media_type="image/png")


###############
#  ADMIN API  #
###############
@app.get(
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


@app.delete(
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


@app.delete(
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


@app.delete(
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
