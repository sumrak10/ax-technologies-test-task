import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import ForeignKey, ARRAY, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.metadata import Base
from src.database.sqla_types import int_pk_c, str256_c, str512_c, created_at_c, str32_c
from src.models import books_users_association_table
from src.schemas.users import UserDTO, UserAPIKeyDTO

if TYPE_CHECKING:
    from src.models import Books


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int_pk_c]
    name: Mapped[str256_c]
    email: Mapped[str512_c] = mapped_column(unique=True)
    username: Mapped[str256_c] = mapped_column(unique=True)
    password: Mapped[str512_c]
    banned: Mapped[bool] = mapped_column(default=False)
    permissions: Mapped[dict[str, Any]]
    excluded_categories: Mapped[set[str]] = mapped_column(ARRAY(String), default=[])
    created_at: Mapped[created_at_c]

    api_keys: Mapped[list['UserAPIKeys']] = relationship(back_populates='user', lazy='noload')

    books: Mapped[set['Books']] = relationship(
        secondary=books_users_association_table, back_populates="users"
    )

    def to_DTO(self, with_password: bool = False) -> UserDTO:
        return UserDTO(
            id=self.id,
            name=self.name,
            email=self.email,
            username=self.username,
            password=self.password if with_password else None,
            banned=self.banned,
            permissions=self.permissions,
            excluded_categories=self.excluded_categories,
            created_at=self.created_at,
            api_keys=[api_key.to_DTO() for api_key in self.api_keys] if self.api_keys else None
        )


class UserAPIKeys(Base):
    __tablename__ = 'user_api_keys'

    id: Mapped[int_pk_c]
    key: Mapped[str32_c]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    expire_date: Mapped[datetime.date]
    created_at: Mapped[created_at_c]

    user: Mapped['Users'] = relationship(back_populates='api_keys', lazy='noload')

    def to_DTO(self) -> UserAPIKeyDTO:
        return UserAPIKeyDTO(
            id=self.id,
            key=self.key,
            user_id=self.user_id,
            expire_date=self.expire_date,
            created_at=self.created_at,
            user=self.user.to_DTO() if self.user else None
        )
