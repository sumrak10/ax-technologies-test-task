from sqlalchemy import and_

from src.models import books_users_association_table
from src.utils.repository import SQLAlchemyRepository, select
from src.models.users import *


class UsersRepository(SQLAlchemyRepository[UserDTO]):
    model = Users

    async def get_one_by_username(self, username: str, with_password: bool = False) -> UserDTO | None:
        stmt = select(self.model).filter_by(username=username)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        return None if res is None else res.to_DTO(with_password)

    async def add_book(self, user_id: int, book_id: int) -> None:
        stmt = books_users_association_table.insert().values(user_id=user_id, book_id=book_id)
        await self.session.execute(stmt)

    async def del_book(self, user_id: int, book_id: int) -> None:
        stmt = books_users_association_table.delete().where(
            and_(books_users_association_table.c.user_id == user_id,
                 books_users_association_table.c.book_id == book_id)
        )
        await self.session.execute(stmt)


class UserAPIKeysRepository(SQLAlchemyRepository[UserAPIKeyDTO]):
    model = UserAPIKeys
