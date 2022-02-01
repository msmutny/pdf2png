import uuid

from flask import Blueprint, jsonify
from flask_pydantic import validate
from sqlmodel import Session

from app.config.db import get_session
from app.services import service


admin_route = Blueprint('admin_route', __name__)


@admin_route.route("/documents", methods=["GET"])
@validate()
def get_documents():
    session: Session = next(get_session())
    return jsonify([d.dict() for d in service.get_documents(session)])


@admin_route.route("/documents", methods=["DELETE"])
@validate()
def delete_documents():
    session: Session = next(get_session())
    return service.delete_documents(session)


@admin_route.route("/documents/<id>", methods=["DELETE"])
@validate()
def delete_document(id):
    session: Session = next(get_session())
    document_id = uuid.UUID(id)
    return service.delete_document(session, document_id)


@admin_route.route("/documents/<id>/pages", methods=["DELETE"])
@validate()
def delete_pages(id):
    session: Session = next(get_session())
    document_id = uuid.UUID(id)
    return service.delete_pages(session, document_id)
