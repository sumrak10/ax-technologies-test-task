import enum
from datetime import datetime
from typing import Annotated

from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import mapped_column

int_pk_c = Annotated[int, mapped_column(primary_key=True)]
str_pk_c = Annotated[str, mapped_column(primary_key=True)]

str2_c = Annotated[str, mapped_column(String(2))]
str16_c = Annotated[str, mapped_column(String(16))]
str32_c = Annotated[str, mapped_column(String(32))]
str64_c = Annotated[str, mapped_column(String(64))]
str256_c = Annotated[str, mapped_column(String(256))]
str512_c = Annotated[str, mapped_column(String(512))]

datetime_c = Annotated[datetime, mapped_column(DateTime())]
created_at_c = Annotated[datetime, mapped_column(DateTime(), server_default=text("TIMEZONE('utc', now())"))]
