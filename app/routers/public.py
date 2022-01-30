import io
from typing import Optional

from fastapi import HTTPException, status, UploadFile, File, Path, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import UUID4

from app import schemas
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
def create_document(file: UploadFile = File(...), normalize: Optional[bool] = True):
    return service.process_document(
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
def get_document(id: UUID4):
    return service.get_document(id)


@router.get(
    "/documents/{id:uuid}/pages/{page_number:int}",
    tags=["Public"],
    response_class=StreamingResponse
)
def get_page(id: UUID4, page_number: int = Path(..., ge=1)):
    image: bytes = service.get_page(id, page_number)
    return StreamingResponse(io.BytesIO(image), media_type="image/png")
