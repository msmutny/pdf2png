import warnings

import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.config.db import get_session
from app.main import app

# TODO - complete integration tests - use the dramatiq mock to mimic the real behavior


@pytest.fixture(name="silence_sa_warning")
def silence_warning_fixture():
    """
    Fixture for silencing the SA warning. For details see #https://github.com/tiangolo/sqlmodel/issues/189
    """
    warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


@pytest.fixture(name="session")
def session_fixture():
    """
    Reusable session with in-memory sqlite database
    """
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def fixture_client(session, silence_sa_warning):
    """
    Reusable client as a fixture
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()


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

