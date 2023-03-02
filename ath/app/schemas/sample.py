import datetime as dt
import uuid
from typing import List, Optional

import pytz
from pydantic import BaseModel, Extra
from sqlalchemy import null
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, func, text

from app.enums.sample import Status
from app.schemas.base import Base
from app.schemas.summary_statistics import SummaryStatisticsDb, SummaryStatisticsDbRead
from app.schemas.visualization import VisualizationDb, VisualizationRead

# Data schemas #######################################


class SampleBase(SQLModel):
    started_upload_at: Optional[dt.datetime] = Field(
        default_factory=lambda: dt.datetime.now(tz=pytz.utc)
    )
    finished_upload_at: Optional[dt.datetime] = None
    status: Status

    upload_id: uuid.UUID
    """Generated by the tusd client and added to the request as metadata. This
    is how the api knows, during tusd hebhooks to which sample_id it links
    to."""

    file_name: Optional[str] = Field(default=None)
    """Generated by the tusd client as a name to the file stored in the S3
    server. Can't be used as upload_id since during `pre-create` hook there is
    no ID (file name) yet.
    """

    parsing_error: Optional[str] = Field(default=None)


class SampleDbRead(SampleBase):
    id: uuid.UUID


class SampleDbCreate(SampleBase, extra=Extra.forbid):
    ...


class SampleDbUpdate(SQLModel):
    started_upload_at: Optional[dt.datetime]
    finished_upload_at: Optional[dt.datetime]
    status: Optional[Status]
    upload_id: Optional[uuid.UUID]
    file_name: Optional[str]
    parsing_error: Optional[str]


class SampleDb(Base, SampleBase, table=True):
    __tablename__ = "sample"

    upload_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), nullable=False, unique=True)
    )

    started_upload_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    visualization: "VisualizationDb" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="sample"
    )

    summary_statistics: "SummaryStatisticsDb" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="sample"
    )


# Service schemas #######################################


class SampleRead(SampleDbRead):
    summary_statistics: Optional[SummaryStatisticsDbRead] = Field(None)
    visualization: Optional[VisualizationRead] = Field(None)


# Routes schemas #######################################


class SampleReadListResponse(BaseModel):
    sample_reads: List[SampleRead]