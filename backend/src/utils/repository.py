from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy import Table, insert, select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import async_session_maker
from src.database.metadata import Base

SchemaType = TypeVar('SchemaType', bound=BaseModel)

class AbstractRepository(ABC):
    @abstractmethod
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def add_one(self, data: dict) -> int:
        pass

    @abstractmethod
    async def edit_one(self, id: int, data: dict) -> int:
        pass

    @abstractmethod
    async def edit_by_filter(self, filters: dict, data: dict) -> None:
        pass

    @abstractmethod
    async def get_one(self, **filter_by) -> SchemaType | None:
        pass

    @abstractmethod
    async def get_all(self) -> list[SchemaType]:
        pass

    @abstractmethod
    async def get_all_with_filters(self, **filter_by) -> list[SchemaType]:
        pass

    @abstractmethod
    async def delete(self, **filter_by) -> None:
        pass


class SQLAlchemyRepository(Generic[SchemaType], AbstractRepository):
    model: Base = None

    def __init__(self, session: AsyncSession | None = None):
        if session is None:
            session = async_session_maker()
        self.session = session

    def commit(self):
        self.session.commit()

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_by_filter(self, filters: dict, data: dict) -> None:
        stmt = update(self.model).values(**data).filter_by(**filters).returning(self.model.id)
        await self.session.execute(stmt)

    async def get_one(self, **filter_by) -> SchemaType | None:
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        return None if res is None else res.to_DTO()

    async def get_all(self) -> list[SchemaType]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return [row[0].to_DTO() for row in res.unique().all()]

    async def get_all_with_filters(self, **filter_by) -> list[SchemaType]:
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return [row[0].to_DTO() for row in res.all()]

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)


class M2MRepository(Generic[SchemaType]):
    def __init__(self, session: AsyncSession, associations_table: Table, schema: BaseModel):
        self.session = session
        self.associations_table = associations_table
        self.schema = schema

    async def get_association(self, left_id: int, right_id: int) -> SchemaType | None:
        stmt = select(self.associations_table).where(
            and_(self.associations_table.c.left_id == left_id,
                 self.associations_table.c.right_id == right_id)
        )
        res = await self.session.execute(stmt)
        res = res.one_or_none()
        return None if res is None else self.schema.model_validate(res, from_attributes=True)
    #
    # async def get_all_associations(self, left_id: int, right_id: int) -> list[SchemaType]:
    #     stmt = select(self.associations_table)
    #     if left_id is not None:
    #         stmt = stmt.where(self.associations_table.c.left_id == left_id)
    #     if right_id is not None:
    #         stmt = stmt.where(self.associations_table.c.right_id == right_id)
    #     res = await self.session.execute(stmt)
    #     return [self.schema.model_validate(row[0], from_attributes=True) for row in res.all()]

    async def add_association(self, left_id: int, right_id: int) -> None:
        stmt = self.associations_table.insert().values(left_id=left_id, right_id=right_id)
        await self.session.execute(stmt)

    async def del_association(self, left_id: int, right_id: int) -> None:
        stmt = self.associations_table.delete().where(
            and_(self.associations_table.c.left_id == left_id,
                 self.associations_table.c.right_id == right_id)
        )
        await self.session.execute(stmt)
