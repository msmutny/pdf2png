from typing import Optional

from sqlmodel import SQLModel


class ItemsToDeleteSchema(SQLModel):
    documents_deleted: Optional[str]
    pages_deleted: str
