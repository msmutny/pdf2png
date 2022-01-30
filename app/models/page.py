from typing import Optional

from pydantic import UUID4
from sqlmodel import Field, SQLModel, Relationship

from app.models.document import Document
from app.utils.utils import generate_uuid


class Page(SQLModel, table=True):
    id: UUID4 = Field(default_factory=generate_uuid, primary_key=True)
    page_number: int = Field()
    image: str = Field()
    document_id: UUID4 = Field(default=None, foreign_key="document.id")
    document: Optional[Document] = Relationship(back_populates="pages")
