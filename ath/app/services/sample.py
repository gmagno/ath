import logging
import uuid
from typing import List, Optional

import pandas as pd
from fastapi import Depends
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config
from app.db.crud.crud_sample import crud_sample
from app.db.session import get_db
from app.enums.sample import Status
from app.error import BadSampleError, ParsingCsvError
from app.schemas.sample import (
    SampleDb,
    SampleDbCreate,
    SampleDbRead,
    SampleDbUpdate,
    SampleRead,
    SampleReadListResponse,
)
from app.schemas.summary_statistics import SummaryStatisticsDbRead
from app.schemas.visualization import VisualizationRead
from app.services.base import BaseService
from app.services.summary_statistics import (
    SummaryStatisticsService,
    get_summary_statistics_service,
)
from app.services.visualization import VisualizationService, get_visualization_service
from app.utils.s3 import s3_csv_url

settings: config.Settings = config.get_settings()

logger: logging.Logger = logging.getLogger(__name__)


class SampleService(BaseService):
    def __init__(
        self,
        db: AsyncSession,
        summary_statistics_svc: SummaryStatisticsService,
        visualization_svc: VisualizationService,
    ) -> None:
        super().__init__(db)
        self.summary_statistics_svc: SummaryStatisticsService = summary_statistics_svc
        self.visualization_svc: VisualizationService = visualization_svc

    async def create(self, sample: SampleDbCreate) -> SampleDbRead:
        sample_db: SampleDb = await crud_sample.create(
            self.db,
            obj_in=sample,
            commit=True,
        )
        sample_db_read: SampleDbRead = SampleDbRead.parse_obj(sample_db)
        return sample_db_read

    async def update_by_upload_id(
        self, upload_id: uuid.UUID, sample_db_update: SampleDbUpdate
    ) -> SampleDbRead:
        sample: Optional[SampleDb] = await crud_sample.get_by_upload_id(
            db=self.db, upload_id=upload_id
        )
        if not sample:
            raise BadSampleError(f"Unable to fetch sample [{upload_id=}]")

        updated_sample: SampleDb = await crud_sample.update(
            db=self.db, db_obj=sample, obj_in=sample_db_update, commit=True
        )
        return SampleDbRead.parse_obj(updated_sample)

    async def get(self, sample_id: uuid.UUID) -> SampleDbRead:
        sample: Optional[SampleDb] = await crud_sample.get(db=self.db, id=sample_id)
        if not sample:
            raise BadSampleError(f"Unable to fetch sample [{sample_id=}]")
        sample_db_read: SampleDbRead = SampleDbRead.parse_obj(sample)
        return sample_db_read

    async def process(self, sample_id: uuid.UUID) -> SampleDbRead:
        sample: Optional[SampleDb] = await crud_sample.get(self.db, id=sample_id)
        if not sample:
            raise BadSampleError(f"Unable to find sample by sample id [{sample_id=}]")

        if not sample.file_name:
            raise BadSampleError(f"Sample has no csv file associated [{sample_id=}]")

        await crud_sample.update(
            db=self.db,
            db_obj=sample,
            obj_in=SampleDbUpdate(status=Status.PARSING),
            commit=True,
        )

        try:
            df: pd.DataFrame = self.read_csv(sample.file_name)
        except ParsingCsvError as e:
            await crud_sample.update(
                db=self.db,
                db_obj=sample,
                obj_in=SampleDbUpdate(status=Status.FAILED, parsing_error=str(e)),
                commit=True,
            )
            return SampleDbRead.parse_obj(sample)

        await crud_sample.update(
            db=self.db,
            db_obj=sample,
            obj_in=SampleDbUpdate(status=Status.PROCESSING),
            commit=True,
        )
        summary_statistics: SummaryStatisticsDbRead = (
            await self.summary_statistics_svc.create(df=df, sample_id=sample.id)
        )

        await crud_sample.update(
            db=self.db,
            db_obj=sample,
            obj_in=SampleDbUpdate(status=Status.RENDERING),
            commit=True,
        )
        visualization: VisualizationRead = await self.visualization_svc.create(
            df=df, sample_id=sample.id
        )

        sample_read: SampleRead = SampleRead(
            **sample.dict(),
            summary_statistics=summary_statistics,
            visualization=visualization,
        )
        await crud_sample.update(
            db=self.db,
            db_obj=sample,
            obj_in=SampleDbUpdate(status=Status.DONE),
            commit=True,
        )
        return sample_read

    def read_csv(self, sample_file_name: str) -> pd.DataFrame:
        url: str = s3_csv_url(sample_file_name)
        dtypes: dict[str, str] = {
            "review_time": "int",
            "merge_time": "int",
            "date": "str",
            "team": "str",
        }
        usecols: list[str] = ["review_time", "merge_time", "team", "date"]
        parse_dates: list[str] = ["date"]
        try:
            df: pd.DataFrame = pd.read_csv(
                url,
                parse_dates=parse_dates,
                usecols=usecols,
                header=0,
                dtype=dtypes,
            )
        except Exception as e:
            raise ParsingCsvError(e)

        return df

    async def list(
        self,
        skip: Optional[int] = 0,
        limit: Optional[int] = 10,
        upload_id: Optional[uuid.UUID] = None,
    ) -> SampleReadListResponse:
        samples: List[
            SampleDb
        ] = await crud_sample.get_multi_by_upload_id_with_relationships(
            db=self.db, skip=skip, limit=limit, upload_id=upload_id
        )
        sample_reads: List[SampleRead] = parse_obj_as(List[SampleRead], samples)
        sample_read_list_response: SampleReadListResponse = SampleReadListResponse(
            sample_reads=sample_reads
        )
        return sample_read_list_response


# Facade #############################


async def create_service(
    db: AsyncSession,
    summary_statistics_svc: SummaryStatisticsService,
    visualization_svc: VisualizationService,
) -> SampleService:
    sample_svc: SampleService = SampleService(
        db, summary_statistics_svc, visualization_svc
    )
    return sample_svc


# Injectable Dependencies ############


async def get_sample_service(
    db: AsyncSession = Depends(get_db),
    summary_statistics_svc: SummaryStatisticsService = Depends(
        get_summary_statistics_service
    ),
    visualization_svc: VisualizationService = Depends(get_visualization_service),
) -> SampleService:
    sample_svc: SampleService = await create_service(
        db, summary_statistics_svc, visualization_svc
    )
    return sample_svc
