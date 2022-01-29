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

app = FastAPI()

# Temporary workaround for #https://github.com/tiangolo/sqlmodel/issues/189
warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


@app.post(
    "/documents-old",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=models.DocumentSchema,
    response_model_include=["id"]
)
def create_document_old(pdf: UploadFile = File(...)):
    content: bytes = pdf.file.read()

    content_base64: bytes = base64.b64encode(content)
    content_base64_decoded: bytes = base64.b64decode(content_base64)
    assert content == content_base64_decoded

    uuid = generate_uuid()
    with Session(engine) as session:
        document = models.Document(id=uuid)
        session.add(document)
        session.commit()

    pages = convert_from_bytes(content, poppler_path=settings.poppler_path)
    images = []
    for page in pages:
        img_byte_arr = io.BytesIO()
        page.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        images.append(img_byte_arr)

    with Session(engine) as session:
        for page_num, image in enumerate(images, start=1):
            page = models.Page(image=base64.b64encode(image), page_number=page_num, document=document)
            session.add(page)

        document = session.get(models.Document, uuid)
        document.status = 'done'
        session.add(document)
        session.commit()
        session.refresh(document)
        document_schema = models.DocumentSchema(**document.dict())
    return document_schema


@app.post(
    "/documents",
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
    "/documents",
    response_model=List[models.Document],
    response_model_exclude=["n_pages"]
)
def get_documents():
    with Session(engine) as session:
        documents = session.exec(
            select(models.Document)
        )
        return documents.all()


@app.get(
    "/documents/{id:uuid}",
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


@app.get("/documents/{id:uuid}/pages/{page_number:int}")
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    #fill_tables_with_data()


# def fill_tables_with_data():
#     with Session(engine) as session:
#         document1 = models.Document()
#         document2 = models.Document()
#         session.add(document1)
#         session.add(document2)
#         session.commit()
#
#         page1_1 = models.Page(image="page1_1_image", page_number=1, document=document1)
#         page1_2 = models.Page(image="page1_2_image", page_number=2, document=document1)
#
#         page2_1 = models.Page(image="page2_1_image", page_number=1, document=document2)
#         page2_2 = models.Page(image="page2_2_image", page_number=2, document=document2)
#         page2_3 = models.Page(image="page2_3_image", page_number=3, document=document2)
#
#         session.add(page1_1)
#         session.add(page1_2)
#         session.add(page2_1)
#         session.add(page2_2)
#         session.add(page2_3)
#         session.commit()
#
#         session.refresh(page1_1)
#         session.refresh(page1_2)
#         session.refresh(page2_1)
#         session.refresh(page2_2)
#         session.refresh(page2_3)
#
#         print("Created page1_1:", page1_1)
#         print("Created page1_2:", page1_2)
#         print("Created page2_1:", page2_1)
#         print("Created page2_2:", page2_2)
#         print("Created page2_3:", page2_3)

