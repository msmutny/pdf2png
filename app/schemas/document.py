from typing import Optional

from pydantic import UUID4
from sqlmodel import SQLModel


class DocumentSchema(SQLModel):
    id: UUID4
    status: str
    n_pages: Optional[int] = None
