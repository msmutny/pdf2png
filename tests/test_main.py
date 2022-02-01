from fastapi.testclient import TestClient


# TODO - complete integration tests - use the dramatiq mock to mimic the real behavior


def test_get_documents_from_empty_database(client: TestClient):
    response = client.get("/documents/")
    data = response.json()
    assert response.status_code == 200
    assert data == []


def test_get_non_existing_document(client: TestClient):
    response = client.get("/documents/123")
    assert response.status_code == 404


def test_get_page_in_non_existing_document(client: TestClient):
    response = client.get("/documents/123/pages/1")
    assert response.status_code == 404


# def test_upload_pdf_document_and_check_status(client: TestClient):
#     response = client.post(
#         "/documents",
#         files={"file": ("filename", open("tests/resources/factoring_lab.pdf", "rb"), "application/pdf")}
#     )
#     assert response.status_code == 202
#     data = response.json()
#     assert 'id' in data
#     document_id = data['id']
#
#     response = client.get(f"/documents/{document_id}")
#     assert response.status_code == 200
#     data = response.json()
#     assert 'status' in data
#     assert 'n_pages' in data
#     assert data['status'] == 'processing'
#     assert data['n_pages'] == 0


def test_upload_non_pdf_document(client: TestClient):
    response = client.post(
        "/documents",
        files={"file": ("filename", open("tests/resources/non-pdf-file.txt", "rb"), "text/plain")}
    )
    assert response.status_code == 415


# def test_upload_non_pdf_document_as_pdf_type(client: TestClient):
#     """
#     We 'promise' to send a PDF file, but the actual content is a plain text file, so the endpoint accepts it,
#     returns 202 ACCEPTED and then later the rabbitmq worker finds out that the content is a malicious PDF file
#     and updates the record in the database to 'status=error'
#     """
#     response = client.post(
#         "/documents",
#         files={"file": ("filename", open("tests/resources/non-pdf-file.txt", "rb"), "application/pdf")}
#     )
#     assert response.status_code == 202

