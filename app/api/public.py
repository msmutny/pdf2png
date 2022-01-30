import io
import base64
from typing import Optional

from fastapi import HTTPException, status, UploadFile, File, Path, APIRouter
from pydantic import UUID4
from sqlmodel import Session, select
from starlette.responses import StreamingResponse
from sqlalchemy import func

from app import models
from app.db import engine
from app.utils import generate_uuid
from app.worker import convert_document


router = APIRouter()


@router.post(
    "/documents",
    tags=["Public"],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=models.DocumentSchema,
    response_model_include=["id"]
)
def create_document(file: UploadFile = File(...), normalize: Optional[bool] = True):
    content: bytes = file.file.read()
    content_base64_encoded_bytes: bytes = base64.b64encode(content)
    document_base64_encoded_string: str = content_base64_encoded_bytes.decode('ascii')

    uuid = generate_uuid()
    with Session(engine) as session:
        document = models.Document(id=uuid)
        session.add(document)
        session.commit()
        session.refresh(document)
        document_schema = models.DocumentSchema(**document.dict())

    convert_document.send(str(uuid), document_base64_encoded_string, normalize)

    return document_schema


@router.get(
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


@router.get(
    "/documents/{id:uuid}/pages/{page_number:int}",
    tags=["Public"],
)
def get_page(id: UUID4, page_number: int = Path(..., ge=1)):
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
