from datetime import datetime
from typing import Optional

from pydantic import UUID4
from sqlmodel import SQLModel


class DocumentSchema(SQLModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    status: str
    filename: str
    n_pages: Optional[int] = None
