from abc import abstractmethod
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.types import JSON

from src.database.sqla_types import int_pk_c


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON,
    }

    id: Mapped[int_pk_c]

    @abstractmethod
    def to_DTO(self) -> BaseModel:
        raise NotImplementedError

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
