import io
import logging
import uuid
from typing import Any, List, Literal, Optional, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from fastapi import Depends
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.crud.crud_sample import crud_sample
from app.db.crud.crud_visualization import crud_visualization
from app.db.session import get_db
from app.error import BadSampleError
from app.schemas.plots import PlotDb, PlotDbRead
from app.schemas.sample import SampleDb
from app.schemas.visualization import (
    NamedFigure,
    VisualizationDb,
    VisualizationDbCreate,
    VisualizationRead,
)
from app.services.base import BaseService
from app.utils.s3 import s3_upload_file_from_memory

logger: logging.Logger = logging.getLogger(__name__)
settings: Settings = get_settings()


class VisualizationService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def create(self, df: pd.DataFrame, sample_id: uuid.UUID) -> VisualizationRead:
        sample: Optional[SampleDb] = await crud_sample.get(db=self.db, id=sample_id)
        if not sample:
            raise BadSampleError(f"Unable to fetch sample by sample id [{sample_id=}]")

        named_figures: List[NamedFigure] = self.create_named_figures(df)

        self.upload_named_figures_to_s3(
            named_figures=named_figures, sample_file_name=cast(str, sample.file_name)
        )

        def get_plot_file_name(named_figure_name: str) -> str:
            return (
                f"{sample.file_name}"  # type: ignore
                f"/{named_figure_name}"
                f".{settings.VISUALIZATION_RENDERING_FORMAT}"
            )

        plots: List[PlotDb] = [
            PlotDb(
                file_name=get_plot_file_name(named_figure.name),
                url=self.gen_plot_url(file_name=get_plot_file_name(named_figure.name)),
            )
            for named_figure in named_figures
        ]
        visualization_db: VisualizationDb = await crud_visualization.create_with_plots(
            self.db,
            obj_in=VisualizationDbCreate(),
            sample=sample,
            plots=plots,
            commit=True,
        )

        plots_db_read: List[PlotDbRead] = parse_obj_as(List[PlotDbRead], plots)

        visualization_read: VisualizationRead = VisualizationRead(
            id=visualization_db.id, plots=plots_db_read
        )
        return visualization_read

    def gen_plot_url(self, file_name: str) -> str:
        url: str = (
            f"http://"
            f"{settings.S3_HOST_EXT}"
            f":{settings.S3_PORT_EXT}"
            f"/{settings.S3_PLOTS_BUCKET_NAME}"
            f"/{file_name}"
        )
        return url

    def create_named_figures(self, df: pd.DataFrame) -> List[NamedFigure]:
        mean_time_with_outliers_stacked_bar_plotfig: NamedFigure = (
            self.create_mean_time_stacked_bar_fig(df)
        )
        mean_time_no_outliers_stacked_bar_plotfig: NamedFigure = (
            self.create_mean_time_stacked_bar_fig(df, include_outliers=False)
        )
        num_prs_by_team_pie_chart_plotfig: NamedFigure = (
            self.create_num_prs_by_team_pie_chart_fig(df)
        )
        num_prs_by_team_no_outliers_pie_chart_plotfig: NamedFigure = (
            self.create_num_prs_by_team_pie_chart_fig(df, include_outliers=False)
        )
        review_time_distribution_violin_plotfig: NamedFigure = (
            self.create_time_distribution_violin_fig(df, column="review_time")
        )
        merge_time_distribution_violin_plotfig: NamedFigure = (
            self.create_time_distribution_violin_fig(df, column="merge_time")
        )
        review_time_distribution_no_outliers_violin_plotfig: NamedFigure = (
            self.create_time_distribution_violin_fig(
                df, column="review_time", include_outliers=False
            )
        )
        merge_time_distribution_no_outliers_violin_plotfig: NamedFigure = (
            self.create_time_distribution_violin_fig(
                df, column="merge_time", include_outliers=False
            )
        )

        named_figures: List[NamedFigure] = [
            mean_time_with_outliers_stacked_bar_plotfig,
            mean_time_no_outliers_stacked_bar_plotfig,
            num_prs_by_team_pie_chart_plotfig,
            num_prs_by_team_no_outliers_pie_chart_plotfig,
            review_time_distribution_violin_plotfig,
            merge_time_distribution_violin_plotfig,
            review_time_distribution_no_outliers_violin_plotfig,
            merge_time_distribution_no_outliers_violin_plotfig,
        ]
        return named_figures

    def upload_named_figures_to_s3(
        self, named_figures: List[NamedFigure], sample_file_name: str
    ) -> None:
        for named_figure in named_figures:
            fig_data: bytes = self.render_fig_to_memory(named_figure.figure)
            plot_name: str = (
                f"{sample_file_name}"
                f"/{named_figure.name}"
                f".{settings.VISUALIZATION_RENDERING_FORMAT}"
            )
            # self.s3_upload_file_from_memory(
            #     fig_data, plot_name, settings.S3_PLOTS_BUCKET_NAME
            # )
            s3_upload_file_from_memory(
                fig_data, plot_name, settings.S3_PLOTS_BUCKET_NAME
            )

    def create_mean_time_stacked_bar_fig(
        self, df: pd.DataFrame, include_outliers=True
    ) -> NamedFigure:
        title = "Mean review and merge time by team"
        outlier_token = "with_outliers" if include_outliers else "no_outliers"
        filename: str = f"mean_time_{outlier_token}_stacked_bar_plot"

        sub: pd.DataFrame = df[["review_time", "merge_time", "team"]]
        if not include_outliers:
            title += "\nexcluding unreviewed and non-CI PRs"
            sub = sub[(sub.review_time != 0) & (sub.merge_time != 0)]

        mean_df: pd.DataFrame = sub.groupby(by="team").mean()
        bar_plot: Axes = mean_df.plot(kind="bar", stacked=True, title=title)
        bar_plot.set_xticklabels(bar_plot.get_xticklabels(), rotation=35, ha="right")
        bar_plot.set_ylabel("time (s)")
        fig: Figure = bar_plot.get_figure()
        fig.tight_layout()
        return NamedFigure(figure=fig, name=filename)

    def create_num_prs_by_team_pie_chart_fig(
        self, df: pd.DataFrame, include_outliers=True
    ) -> NamedFigure:
        title = "Number of PRs by team"
        outlier_token = "with_outliers" if include_outliers else "no_outliers"
        filename: str = f"num_prs_by_team_{outlier_token}_pie_chart_plot"
        sub = df
        if not include_outliers:
            title += "\nexcluding unreviewed and non-CI PRs"
            sub = df[(df.review_time != 0) & (df.merge_time != 0)]
        num_prs: pd.Series[int] = sub.groupby(by="team").size()
        fig: Figure = plt.figure()

        def func(pct: int, vals):
            # FIXME: I should directly extract the number of PRs instead of computing it
            absolute = int(np.round(pct / 100.0 * vals.sum()))
            return f"{pct:.1f}%\n({absolute:d} PRs)"

        num_prs.plot(
            kind="pie", y="team", title=title, autopct=lambda pct: func(pct, num_prs)
        )
        fig.tight_layout()
        return NamedFigure(figure=fig, name=filename)

    def create_time_distribution_violin_fig(
        self,
        df: pd.DataFrame,
        column: Literal["review_time", "merge_time"],
        include_outliers=True,
    ) -> NamedFigure:
        title = "Review" if column == "review_time" else "Merge"
        title += " time distribution by team"
        outlier_token = "with_outliers" if include_outliers else "no_outliers"
        filename: str = f"{column}_distribution_{outlier_token}_violin_plot"
        sub = df
        if not include_outliers:
            title += "\nexcluding unreviewed and non-CI PRs"
            sub = df[(df.review_time != 0) & (df.merge_time != 0)]

        fig: Figure = plt.figure()
        sub = sub[(sub.review_time != 0) & (sub.merge_time != 0)]
        violin_plot = sns.violinplot(data=sub, y=column, x="team", cut=0)
        violin_plot.set_title(title)
        violin_plot.set_ylabel("time (s)")
        fig.tight_layout()
        return NamedFigure(figure=fig, name=filename)

    def render_fig_to_memory(self, fig: Figure) -> bytes:
        buf: io.BytesIO = io.BytesIO()
        fig.savefig(buf, format=f"{settings.VISUALIZATION_RENDERING_FORMAT}")
        buf.seek(0)
        data: bytes = buf.getvalue()
        buf.close()
        return data

    # def s3_upload_file_from_memory(
    #     self, data: bytes, file_name: str, bucket: str
    # ) -> None:
    #     s3_url: str = f"http://" f"{settings.S3_HOST}:{settings.S3_PORT}"
    #     s3 = boto3.resource(
    #         "s3",
    #         endpoint_url=s3_url,
    #         region_name=settings.S3_REGION,
    #         aws_access_key_id=settings.S3_ACCESS_KEY,
    #         aws_secret_access_key=settings.S3_SECRET_KEY,
    #     )
    #     client: Any = s3.meta.client
    #     with io.BytesIO(data) as f:
    #         client.upload_fileobj(f, bucket, file_name)


# Facade #############################


async def create_service(db: AsyncSession) -> VisualizationService:
    visualization_svc: VisualizationService = VisualizationService(db)
    return visualization_svc


# Injectable Dependencies ############


async def get_visualization_service(
    db: AsyncSession = Depends(get_db),
) -> VisualizationService:
    visualization_svc: VisualizationService = await create_service(db)
    return visualization_svc
