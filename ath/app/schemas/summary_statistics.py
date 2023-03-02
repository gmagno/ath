import datetime as dt
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, validator
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.schemas.base import Base

# Service schemas #######################################


class DateInterval(BaseModel):
    begin: dt.datetime
    end: dt.datetime


class TimesScalar(BaseModel):
    review_time: float
    merge_time: float
    total_time: float

    @validator("review_time", "merge_time", "total_time", pre=True)
    def parse_field(cls, value: Any) -> float:
        try:
            return round(float(value), 1)
        except TypeError:
            return round(float(min(value)), 1)


class GroupStats(BaseModel):
    mean: TimesScalar
    mode: TimesScalar
    median: TimesScalar
    count: int


class NumMissingValues(BaseModel):
    review_time: int
    merge_time: int
    date: int
    team: int


class Report(BaseModel):
    total_num_observations: int
    teams: List[str]
    date_interval: DateInterval
    stats: GroupStats
    per_team: Optional[Dict[str, GroupStats]]
    num_prs_without_review: int
    num_prs_without_ci: int
    num_missing_values: NumMissingValues


# Data schemas #######################################


class SummaryStatisticsBase(SQLModel):
    report: Report


class SummaryStatisticsDbRead(SummaryStatisticsBase):
    id: uuid.UUID


class SummaryStatisticsDbCreate(SummaryStatisticsBase, extra=Extra.forbid):
    ...


class SummaryStatisticsDbUpdate(SQLModel):
    ...


class SummaryStatisticsDb(Base, SummaryStatisticsBase, table=True):
    __tablename__ = "summary_statistics"

    report: Dict = Field(default={}, sa_column=Column(JSON))  # type: ignore

    sample_id: uuid.UUID = Field(foreign_key="sample.id", nullable=True, default=None)
    sample: "SampleDb" = Relationship(back_populates="summary_statistics")


# Routes schemas #######################################
