from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, relationship

from src.database.metadata import Base
from src.database.sqla_types import int_pk_c, str2_c, str16_c, str256_c, str512_c, datetime_c
from src.schemas.books import BookDTO

if TYPE_CHECKING:
    from src.models import Users

books_users_association_table = Table(
    "books_users_associations",
    Base.metadata,
    Column("left_id", ForeignKey("books.id"), primary_key=True),
    Column("right_id", ForeignKey("users.id"), primary_key=True),
)


class Books(Base):
    __tablename__ = 'books'

    id: Mapped[int_pk_c]
    gb_id: Mapped[str16_c]
    ISBN: Mapped[str | None]
    title: Mapped[str256_c | None]
    subtitle: Mapped[str | None]
    description: Mapped[str | None]
    language: Mapped[str2_c | None]
    pub_date: Mapped[str | None]

    categories: Mapped[str]

    authors: Mapped[str]

    users: Mapped[set['Users']] = relationship(
        secondary=books_users_association_table, back_populates="books", lazy='noload'
    )

    def to_DTO(self) -> BookDTO:
        return BookDTO(
            id=self.id,
            gb_id=self.gb_id,
            ISBN=self.ISBN,
            title=self.title,
            subtitle=self.subtitle,
            description=self.description,
            language=self.language,
            pub_date=self.pub_date,
            categories=self.categories,
            authors=self.authors,
        )
