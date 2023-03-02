import uuid
from typing import TYPE_CHECKING, Optional

from pydantic import Extra
from sqlmodel import Field, Relationship, SQLModel

from app.schemas.base import Base

if TYPE_CHECKING:
    from app.schemas.visualization import VisualizationDb


class PlotBase(SQLModel):
    file_name: str
    url: str


class PlotDbRead(PlotBase):
    id: uuid.UUID


class PlotDbCreate(PlotBase, extra=Extra.forbid):
    ...


class PlotDbUpdate(SQLModel):
    file_name: Optional[str]


class PlotDb(Base, PlotBase, table=True):
    __tablename__ = "plot"

    visualization_id: uuid.UUID = Field(default=None, foreign_key="visualization.id")
    visualization: "VisualizationDb" = Relationship(back_populates="plots")


# Routes schemas #######################################
