import datetime

from pydantic import BaseModel


class BookUserAssociationDTO(BaseModel):
    left_id: int
    right_id: int


# CATEGORI

# BOOKS
class BookDTO(BaseModel):
    id: int
    gb_id: str
    ISBN: str | None
    title: str | None
    subtitle: str | None
    description: str | None
    language: str
    pub_date: str | None

    categories: str

    authors: str


class BookCreateSchema(BaseModel):
    gb_id: str
    ISBN: str | None
    title: str | None
    subtitle: str | None
    description: str | None
    language: str | None
    pub_date: str | None


class BookAPISchema(BookCreateSchema):
    categories: str | None
    authors: str | None
