from datetime import datetime
from typing import List

from pydantic import UUID4
from sqlmodel import Field, SQLModel, Relationship

from app.utils.utils import generate_uuid


class Document(SQLModel, table=True):
    id: UUID4 = Field(default_factory=generate_uuid, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default='processing')
    filename: str = Field()
    pages: List["Page"] = Relationship(back_populates="document")
