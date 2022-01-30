import base64
import uuid


def generate_uuid() -> uuid.UUID:
    # Note: Work around UUIDs with leading zeros: https://github.com/tiangolo/sqlmodel/issues/25
    # by making sure uuid str does not start with a leading 0
    val = uuid.uuid4()
    while val.hex[0] == '0':
        val = uuid.uuid4()
    return val


def bytes_to_base64_encoded_string(data: bytes) -> str:
    data_base64_encoded_bytes: bytes = base64.b64encode(data)
    data_base64_encoded_string: str = data_base64_encoded_bytes.decode('ascii')
    return data_base64_encoded_string


def base64_encoded_string_to_bytes(string: str) -> bytes:
    data_base64_encoded_bytes: bytes = string.encode('ascii')
    data_base64_decoded: bytes = base64.b64decode(data_base64_encoded_bytes)
    return data_base64_decoded
