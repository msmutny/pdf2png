import warnings

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import create_engine, SQLModel, Session
from starlette.testclient import TestClient

from app.config.db import get_session
from app.main import app


@pytest.fixture(name="silence_sa_warning")
def silence_warning_fixture():
    """
    Fixture for silencing the SA warning. For details see #https://github.com/tiangolo/sqlmodel/issues/189
    """
    warnings.filterwarnings("ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*")


@pytest.fixture(name="session")
def session_fixture(silence_sa_warning):
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
def fixture_client(session):
    """
    Reusable client as a fixture
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()
