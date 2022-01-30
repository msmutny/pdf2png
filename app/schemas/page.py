from pydantic import UUID4
from sqlmodel import SQLModel


class PageSchema(SQLModel):
    id: UUID4
    page_number: int
