import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import CRUDBase
from app.schemas.sample import SampleDb
from app.schemas.summary_statistics import (
    SummaryStatisticsDb,
    SummaryStatisticsDbCreate,
    SummaryStatisticsDbUpdate,
)

logger: logging.Logger = logging.getLogger(__name__)


class CRUDSummaryStatistics(
    CRUDBase[SummaryStatisticsDb, SummaryStatisticsDbCreate, SummaryStatisticsDbUpdate]
):
    async def create(  # type: ignore
        self,
        db: AsyncSession,
        obj_in: SummaryStatisticsDbCreate,
        sample: SampleDb,
        flush: bool = True,
        commit: bool = False,
    ) -> SummaryStatisticsDb:
        report = json.loads(obj_in.report.json())
        db_obj = SummaryStatisticsDb(report=report, sample=sample)  # type: ignore
        db.add(db_obj)
        if flush:
            await db.flush()
        if commit:
            await db.commit()
        return db_obj


crud_summary_statistics: CRUDSummaryStatistics = CRUDSummaryStatistics(
    SummaryStatisticsDb
)
