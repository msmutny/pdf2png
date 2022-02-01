import io

from flask import request, abort, send_file, Blueprint
from flask_pydantic import validate
from pydantic import BaseModel
from sqlmodel import Session
from starlette import status

from app import schemas
from app.config.db import get_session
from app.services import service
from app.utils.utils import generate_uuid


public_route = Blueprint('public_route', __name__)


class CreateDocumentQueryModel(BaseModel):
    normalize: bool = True


@public_route.route("/documents", methods=["POST"])
@validate()
def create_document(query: CreateDocumentQueryModel):
    if 'file' not in request.files:
        abort(status.HTTP_422_UNPROCESSABLE_ENTITY)
    file = request.files['file']
    if file.content_type != 'application/pdf':
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    session: Session = next(get_session())
    return service.process_document(
        session,
        data=file.read(),
        filename=file.filename,
        document_id=generate_uuid(),
        normalize=query.normalize
    )


@public_route.route("/documents/<id>", methods=["GET"])
@validate()
def get_document(id):
    session: Session = next(get_session())
    document: schemas.DocumentSchema = service.get_document(session, id)
    if not document:
        abort(status.HTTP_404_NOT_FOUND)
    return document


@public_route.route("/documents/<id>/pages/<page_number>", methods=["GET"])
@validate()
def get_page(id, page_number):
    page_number = int(page_number)
    session: Session = next(get_session())
    image: bytes = service.get_page(session, id, page_number)
    if not image:
        abort(status.HTTP_404_NOT_FOUND)
    return send_file(io.BytesIO(image), mimetype='image/png')