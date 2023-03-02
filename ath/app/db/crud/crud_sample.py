import logging
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlmodel import select

from app.db.crud import CRUDBase
from app.schemas.sample import SampleDb, SampleDbCreate, SampleDbUpdate
from app.schemas.summary_statistics import SummaryStatisticsDb
from app.schemas.visualization import VisualizationDb

logger = logging.getLogger(__name__)


class CRUDSample(CRUDBase[SampleDb, SampleDbCreate, SampleDbUpdate]):
    async def get_by_upload_id(
        self, db: AsyncSession, upload_id: uuid.UUID
    ) -> Optional[SampleDb]:
        result = await db.execute(
            select(SampleDb).where(SampleDb.upload_id == upload_id)
        )
        sample = result.scalars().one_or_none()
        return sample

    async def get_multi_by_upload_id(
        self,
        db: AsyncSession,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
        upload_id: Optional[uuid.UUID] = None,
    ) -> List[SampleDb]:
        stmt = select(SampleDb).offset(skip)
        if limit:
            stmt = stmt.limit(limit)
        if upload_id:
            stmt = stmt.where(SampleDb.upload_id == upload_id)
        result = await db.execute(stmt)
        entries = result.scalars()
        return list(entries)

    async def get_multi_by_upload_id_with_relationships(
        self,
        db: AsyncSession,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
        upload_id: Optional[uuid.UUID] = None,
    ) -> List[SampleDb]:
        stmt = (
            select(SampleDb)
            .offset(skip)
            .options(joinedload(SampleDb.summary_statistics))
            .options(
                joinedload(SampleDb.visualization).joinedload(VisualizationDb.plots)
            )
        )
        if limit:
            stmt = stmt.limit(limit)
        if upload_id:
            stmt = stmt.where(SampleDb.upload_id == upload_id)

        result = await db.execute(stmt)
        entries = result.scalars().unique().all()
        return entries


crud_sample = CRUDSample(SampleDb)
