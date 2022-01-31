from sqlmodel import SQLModel, create_engine, Session
from app.config.settings import settings

engine = create_engine(settings.database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
