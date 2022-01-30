import base64
import io
import logging
import uuid
from collections import namedtuple
from urllib.parse import urlparse

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from pdf2image import convert_from_bytes
from sqlmodel import Session
from PIL import Image

from app import models
from app.db import engine
from app.settings import settings

# redis_parameters = urlparse(settings.redis_url)
# redis_broker = RedisBroker(
#     host=redis_parameters.hostname,
#     port=redis_parameters.port,
#     username=redis_parameters.username,
#     password=redis_parameters.password,
#     ssl=redis_parameters.scheme == "rediss",
#     ssl_cert_reqs=None,
# )
rabbitmq_broker = RabbitmqBroker(
    host=settings.rabbitmq_host
)

dramatiq.set_broker(rabbitmq_broker)
#dramatiq.set_broker(redis_broker)


@dramatiq.actor
def convert_document(document_id_str: str, document_base64_encoded_string: str, normalize=True):
    document_id: uuid.UUID = uuid.UUID(document_id_str)
    document_base64_encoded_bytes: bytes = document_base64_encoded_string.encode('ascii')
    content_base64_decoded: bytes = base64.b64decode(document_base64_encoded_bytes)

    pages = convert_from_bytes(content_base64_decoded, poppler_path=settings.poppler_path)
    images = []
    for page in pages:
        if normalize:
            page = normalize_image(page)
        img_byte_arr = io.BytesIO()
        page.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        images.append(img_byte_arr)

    with Session(engine) as session:
        document = session.get(models.Document, document_id)
        if not document:
            logging.error(f"Cannot find document with ID {document_id} in the database!")
            return

        for page_num, image in enumerate(images, start=1):
            page = models.Page(image=base64.b64encode(image), page_number=page_num, document=document)
            session.add(page)

        document.status = 'done'
        session.add(document)
        session.commit()


CropBox = namedtuple('CropBox', 'x y')
crop_box = CropBox(x=1200, y=1600)
crop_box_aspect_ratio = crop_box.x / crop_box.y


def normalize_image(image: Image):
    image_aspect_ratio: float = image.size[0] / image.size[1]
    if image_aspect_ratio < crop_box_aspect_ratio:
        x_ratio = crop_box.y / image.size[1]
        normalized_size = (int(image.size[0]*x_ratio), crop_box.y)
    else:
        y_ratio = crop_box.x / image.size[0]
        normalized_size = (crop_box.x, int(image.size[1]*y_ratio))
    assert normalized_size <= crop_box
    return image.resize(normalized_size)
