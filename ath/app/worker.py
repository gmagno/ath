import asyncio
import logging
import uuid
from functools import wraps

from huey import RedisHuey

from app.db.session import async_session_factory, engine
from app.services.sample import SampleService
from app.services.sample import create_service as create_sample_service
from app.services.summary_statistics import SummaryStatisticsService
from app.services.summary_statistics import (
    create_service as create_summary_statistics_service,
)
from app.services.visualization import VisualizationService
from app.services.visualization import create_service as create_visualization_service

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = []


huey: RedisHuey = RedisHuey("nbapi", immediate=False, host="redis")


def run_on_new_event_loop(aio_func):
    @wraps(aio_func)
    def wrapper_decorator(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ret = loop.run_until_complete(aio_func(*args, **kwargs))
        loop.close()

        return ret

    return wrapper_decorator


@huey.task()
@run_on_new_event_loop
async def process_sample(sample_id: uuid.UUID) -> None:
    async with async_session_factory() as db:
        summary_statistics_svc: SummaryStatisticsService = (
            await create_summary_statistics_service(db)
        )
        visualization_svc: VisualizationService = await create_visualization_service(db)
        sample_svc: SampleService = await create_sample_service(
            db, summary_statistics_svc, visualization_svc
        )
        await sample_svc.process(sample_id=sample_id)

    await engine.dispose()
