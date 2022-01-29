from typing import List, Optional

from pydantic import UUID4
from sqlmodel import Field, SQLModel, Relationship

from app.utils import generate_uuid


class DocumentBase(SQLModel):
    id: UUID4 = Field(default_factory=generate_uuid, primary_key=True)
    status: str = Field(default='processing')


class DocumentSchema(DocumentBase):
    n_pages: Optional[int] = None


class Document(DocumentBase, table=True):
    pages: List["Page"] = Relationship(back_populates="document")


class PageBase(SQLModel):
    id: UUID4 = Field(default_factory=generate_uuid, primary_key=True)
    page_number: int = Field()


class PageSchema(PageBase):
    ...


class Page(PageBase, table=True):
    image: str = Field()
    document_id: UUID4 = Field(default=None, foreign_key="document.id")
    document: Optional[Document] = Relationship(back_populates="pages")


