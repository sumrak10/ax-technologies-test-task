from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.repository import SQLAlchemyRepository, M2MRepository
from src.models.books import *
from src.schemas.books import (
    BookDTO,
    BookUserAssociationDTO
)


class BooksRepository(SQLAlchemyRepository[BookDTO]):
    model = Books

    def __init__(self, session: AsyncSession | None = None):
        super().__init__(session)
        self.users_library_repo = M2MRepository(
            self.session, books_users_association_table, BookUserAssociationDTO
        )

    async def get_user_library(self, user_id: int) -> list[BookDTO]:
        stmt = select(Books).join(books_users_association_table).where(
            books_users_association_table.c.right_id == user_id
        )
        res = await self.session.execute(stmt)
        return [row[0].to_DTO() for row in res.all()]

