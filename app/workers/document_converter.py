import io
import logging
import uuid
from collections import namedtuple
from typing import List

import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from pdf2image import convert_from_bytes
import PIL.Image
from pdf2image.exceptions import PDFPageCountError
from pydantic.types import UUID4

from app.config.db import get_session
from app.config.settings import settings
from app.services import crud
from app.utils.utils import base64_encoded_string_to_bytes

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
# dramatiq.set_broker(redis_broker)


ImageSize = namedtuple('ImageSize', 'x y')
crop_box = ImageSize(x=1200, y=1600)
crop_box_aspect_ratio = crop_box.x / crop_box.y


def get_normalized_size(image_size: ImageSize) -> ImageSize:
    image_aspect_ratio = image_size.x / image_size.y
    if image_aspect_ratio < crop_box_aspect_ratio:
        x_ratio = crop_box.y / image_size.y
        return ImageSize(int(image_size.x*x_ratio), crop_box.y)
    else:
        y_ratio = crop_box.x / image_size.x
        return ImageSize(crop_box.x, int(image_size.y*y_ratio))


def convert_pil_image_to_byte_image(pil_image: PIL.Image, normalize: bool) -> bytes:
    if normalize:
        normalized_size = get_normalized_size(ImageSize(*pil_image.size))
        pil_image = pil_image.resize(normalized_size)
    image_bytes_array: io.BytesIO = io.BytesIO()
    pil_image.save(image_bytes_array, format='PNG')
    image_bytes_array: bytes = image_bytes_array.getvalue()
    return image_bytes_array


def convert_pil_images_to_byte_images(pil_images: List["PIL.Image"], normalize: bool) -> List[bytes]:
    return [convert_pil_image_to_byte_image(image, normalize) for image in pil_images]


@dramatiq.actor
def convert_document(document_id_str: str, document_base64_encoded: str, normalize=True):
    document_id: UUID4 = uuid.UUID(document_id_str)
    content_base64_decoded: bytes = base64_encoded_string_to_bytes(document_base64_encoded)
    try:
        pages_pil: List["PIL.Image"] = convert_from_bytes(content_base64_decoded, poppler_path=settings.poppler_path)
    except PDFPageCountError:
        logging.warning(f'Malformed PDF file for document {str(document_id)}')
        crud.update_document_with_status(next(get_session()), document_id=document_id, status='error')
        return
    images_bytes: List[bytes] = convert_pil_images_to_byte_images(pages_pil, normalize)
    crud.add_pages_and_update_document(next(get_session()), document_id, images_bytes)
