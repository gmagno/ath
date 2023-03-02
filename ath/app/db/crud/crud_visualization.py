import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CRUDBase
from app.schemas.plots import PlotDb
from app.schemas.sample import SampleDb
from app.schemas.visualization import (
    VisualizationDb,
    VisualizationDbCreate,
    VisualizationDbUpdate,
)

logger: logging.Logger = logging.getLogger(__name__)


class CRUDVisualization(
    CRUDBase[VisualizationDb, VisualizationDbCreate, VisualizationDbUpdate]
):
    async def create_with_plots(
        self,
        db: AsyncSession,
        obj_in: VisualizationDbCreate,
        sample: SampleDb,
        plots: List[PlotDb],
        flush: bool = True,
        commit: bool = False,
    ) -> VisualizationDb:
        db_obj: VisualizationDb = VisualizationDb(
            **obj_in.dict(), sample=sample, plots=plots
        )
        db.add(db_obj)
        if flush:
            await db.flush()
        if commit:
            await db.commit()
        return db_obj


crud_visualization: CRUDVisualization = CRUDVisualization(VisualizationDb)
