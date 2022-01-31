from app.utils.utils import bytes_to_base64_encoded_string, base64_encoded_string_to_bytes

text_bytes: bytes = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit, " \
                    b"sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
text_base64: str = "TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXBpc2NpbmcgZWxpdCwgc2Vk" \
                   "IGRvIGVpdXNtb2QgdGVtcG9yIGluY2lkaWR1bnQgdXQgbGFib3JlIGV0IGRvbG9yZSBtYWduYSBhbGlxdWEu"


def test_bytes_to_base64_encoded_string():
    assert bytes_to_base64_encoded_string(text_bytes) == text_base64


def test_base64_encoded_string_to_bytes():
    assert base64_encoded_string_to_bytes(text_base64) == text_bytes


def test_bytes_to_base64_and_back():
    text_base64_ = bytes_to_base64_encoded_string(text_bytes)
    text_bytes_ = base64_encoded_string_to_bytes(text_base64_)
    assert text_bytes_ == text_bytes


def test_base64_to_bytes_and_back():
    text_bytes_ = base64_encoded_string_to_bytes(text_base64)
    text_base64_ = bytes_to_base64_encoded_string(text_bytes_)
    assert text_base64_ == text_base64
