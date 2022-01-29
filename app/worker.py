import base64
import io
import uuid
from urllib.parse import urlparse

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from pdf2image import convert_from_bytes
from sqlmodel import Session

from app import models
from app.db import engine
from app.settings import settings

redis_parameters = urlparse(settings.redis_url)
redis_broker = RedisBroker(
    host=redis_parameters.hostname,
    port=redis_parameters.port,
    username=redis_parameters.username,
    password=redis_parameters.password,
    # Heroku Redis with TLS use self-signed certs, so we need to tinker a bit
    ssl=redis_parameters.scheme == "rediss",
    ssl_cert_reqs=None,
)
rabbitmq_broker = RabbitmqBroker(
    host=settings.rabbitmq_host
)

dramatiq.set_broker(rabbitmq_broker)
#dramatiq.set_broker(redis_broker)


@dramatiq.actor
def convert_document(document_id_str: str, document_base64_encoded_string: str):
    document_id: uuid.UUID = uuid.UUID(document_id_str)
    document_base64_encoded_bytes: bytes = document_base64_encoded_string.encode('ascii')
    content_base64_decoded: bytes = base64.b64decode(document_base64_encoded_bytes)

    # TODO - try to save Page into database right after it's been generated
    pages = convert_from_bytes(content_base64_decoded, poppler_path=settings.poppler_path)
    images = []
    for page in pages:
        img_byte_arr = io.BytesIO()
        page.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        images.append(img_byte_arr)

    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        if not document:
            # TODO - use logger
            print(f"Cannot find document with ID {document_id} in the database!")
            return

        for page_num, image in enumerate(images, start=1):
            page = models.Page(image=base64.b64encode(image), page_number=page_num, document=document)
            session.add(page)

        document.status = 'done'
        session.add(document)
        session.commit()
