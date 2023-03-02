import logging
import uuid
from typing import Dict, List, Optional

import pandas as pd
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud.crud_sample import crud_sample
from app.db.crud.crud_summary_statistics import crud_summary_statistics
from app.db.session import get_db
from app.error import BadSampleError
from app.schemas.sample import SampleDb
from app.schemas.summary_statistics import (
    DateInterval,
    GroupStats,
    NumMissingValues,
    Report,
    SummaryStatisticsDb,
    SummaryStatisticsDbCreate,
    SummaryStatisticsDbRead,
)
from app.services.base import BaseService

logger: logging.Logger = logging.getLogger(__name__)


class SummaryStatisticsService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(
        self, df: pd.DataFrame, sample_id: uuid.UUID
    ) -> SummaryStatisticsDbRead:
        total_num_observations: int = self.get_total_num_observations(df)
        teams: list = self.get_teams(df)
        date_interval: DateInterval = self.get_date_interval(df)
        stats: GroupStats = self.get_stats(df)
        per_team: Dict[str, GroupStats] = self.get_per_team_stats(df)
        num_prs_without_review: int = self.get_num_prs_without_review(df)
        num_prs_without_ci: int = self.get_num_prs_without_ci(df)
        num_missing_values: NumMissingValues = self.get_num_missing_values(df)

        report: Report = Report(
            total_num_observations=total_num_observations,
            teams=teams,
            date_interval=date_interval,
            stats=stats,
            per_team=per_team,
            num_prs_without_review=num_prs_without_review,
            num_prs_without_ci=num_prs_without_ci,
            num_missing_values=num_missing_values,
        )

        summary_statistics_db_create: SummaryStatisticsDbCreate = (
            SummaryStatisticsDbCreate(report=report)
        )

        sample: Optional[SampleDb] = await crud_sample.get(db=self.db, id=sample_id)
        if not sample:
            raise BadSampleError(f"Unable to fetch sample [{sample_id=}]")

        summary_statistics_db: SummaryStatisticsDb = (
            await crud_summary_statistics.create(
                db=self.db,
                obj_in=summary_statistics_db_create,
                sample=sample,
                commit=True,
            )
        )

        summary_statistics_db_read: SummaryStatisticsDbRead = (
            SummaryStatisticsDbRead.parse_obj(summary_statistics_db)
        )
        return summary_statistics_db_read

    def get_total_num_observations(self, df: pd.DataFrame) -> int:
        return len(df)

    def get_teams(self, df: pd.DataFrame) -> List[str]:
        return list(df.team.unique())

    def get_date_interval(self, df: pd.DataFrame) -> DateInterval:
        return DateInterval(
            begin=min(df.date).to_pydatetime(),
            end=max(df.date).to_pydatetime(),
        )

    def get_stats(self, df: pd.DataFrame) -> GroupStats:
        sub: pd.DataFrame = df[["review_time", "merge_time"]].copy(deep=True)
        sub["total_time"] = sub["review_time"] + sub["merge_time"]
        mean: pd.Series = sub.mean()
        mode: pd.Series = sub.mode()
        median: pd.Series = sub.median()
        count: int = len(sub)
        sample_stats: GroupStats = GroupStats(
            mean=dict(mean),
            mode=dict(mode),
            median=dict(median),
            count=count,
        )
        return sample_stats

    def get_per_team_stats(self, df: pd.DataFrame) -> Dict[str, GroupStats]:
        sub: pd.DataFrame = df[["review_time", "merge_time", "team"]].copy(deep=True)
        sub["total_time"] = sub["review_time"] + sub["merge_time"]

        mean: pd.DataFrame = sub.groupby(by="team").mean()
        mean_t: pd.DataFrame = mean.transpose()

        mode: pd.DataFrame = sub.groupby(by="team").agg(
            lambda x: min(pd.Series.mode(x))
        )
        mode_t: pd.DataFrame = mode.transpose()

        median: pd.DataFrame = sub.groupby(by="team").median()
        median_t: pd.DataFrame = median.transpose()

        count: pd.Series[int] = sub.groupby(by="team").size()

        teams: List[str] = list(sub.team.unique())

        per_team_stats: dict[str, GroupStats] = {
            team: GroupStats(
                mean=dict(mean_t[team]),
                mode=dict(mode_t[team]),
                median=dict(median_t[team]),
                count=count[team],
            )
            for team in teams
        }
        return per_team_stats

    def get_num_prs_without_review(self, df: pd.DataFrame) -> int:
        num_prs_without_review: int = (df.review_time == 0).sum()
        return num_prs_without_review

    def get_num_prs_without_ci(self, df: pd.DataFrame) -> int:
        num_prs_without_ci: int = (df.merge_time == 0).sum()
        return num_prs_without_ci

    def get_num_missing_values(self, df: pd.DataFrame) -> NumMissingValues:
        num_missing_values: NumMissingValues = NumMissingValues.parse_obj(
            dict(df.isna().sum())
        )
        return num_missing_values


# Facade #############################


async def create_service(db: AsyncSession) -> SummaryStatisticsService:
    summary_statistics_svc: SummaryStatisticsService = SummaryStatisticsService(db)
    return summary_statistics_svc


# Injectable Dependencies ############


async def get_summary_statistics_service(
    db: AsyncSession = Depends(get_db),
) -> SummaryStatisticsService:
    summary_statistics_svc: SummaryStatisticsService = await create_service(db)
    return summary_statistics_svc
