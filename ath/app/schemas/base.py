import datetime as dt
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Column, DateTime, Field, SQLModel, func, text


class Base(SQLModel):
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    )
    id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
