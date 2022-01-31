import io
from typing import Optional

from fastapi import HTTPException, status, UploadFile, File, Path, APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import UUID4
from sqlmodel import Session

from app import schemas
from app.config.db import get_session
from app.services import service
from app.utils.utils import generate_uuid


router = APIRouter()


@router.post(
    "/documents",
    tags=["Public"],
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.DocumentSchema,
    response_model_include=["id"]
)
def create_document(file: UploadFile = File(...),
                    normalize: Optional[bool] = True,
                    session: Session = Depends(get_session)
                    ):
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    return service.process_document(
        session,
        data=file.file.read(),
        filename=file.filename,
        document_id=generate_uuid(),
        normalize=normalize
    )


@router.get(
    "/documents/{id:uuid}",
    tags=["Public"],
    response_model=schemas.DocumentSchema,
    response_model_include=["status", "n_pages"]
)
def get_document(id: UUID4,
                 session: Session = Depends(get_session)
                 ):
    document: schemas.DocumentSchema = service.get_document(session, id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return document


@router.get(
    "/documents/{id:uuid}/pages/{page_number:int}",
    tags=["Public"],
    response_class=StreamingResponse
)
def get_page(id: UUID4,
             page_number: int = Path(..., ge=1),
             session: Session = Depends(get_session)
             ):
    image: bytes = service.get_page(session, id, page_number)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return StreamingResponse(io.BytesIO(image), media_type="image/png")
