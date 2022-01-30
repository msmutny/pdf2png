from typing import List

from pydantic import UUID4
from sqlmodel import Field, SQLModel, Relationship

from app.utils.utils import generate_uuid


class Document(SQLModel, table=True):
    id: UUID4 = Field(default_factory=generate_uuid, primary_key=True)
    status: str = Field(default='processing')
    pages: List["Page"] = Relationship(back_populates="document")
