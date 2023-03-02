import uuid
from typing import TYPE_CHECKING, List, NamedTuple

from matplotlib.figure import Figure
from pydantic import Extra
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.base import Base
from app.schemas.plots import PlotDbRead

if TYPE_CHECKING:
    from app.schemas.plots import PlotDb
    from app.schemas.sample import SampleDb


class VisualizationBase(SQLModel):
    ...


class VisualizationDbRead(VisualizationBase):
    id: uuid.UUID


class VisualizationDbCreate(VisualizationBase, extra=Extra.forbid):
    ...


class VisualizationDbUpdate(SQLModel):
    ...


class VisualizationDb(Base, VisualizationBase, table=True):
    __tablename__ = "visualization"

    sample_id: uuid.UUID = Field(default=None, foreign_key="sample.id")
    sample: "SampleDb" = Relationship(back_populates="visualization")

    plots: List["PlotDb"] = Relationship(back_populates="visualization")


# Service schemas #######################################


class VisualizationRead(VisualizationDbRead):
    plots: List[PlotDbRead]


class NamedFigure(NamedTuple):
    name: str
    figure: Figure
