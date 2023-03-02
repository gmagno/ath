import logging

from fastapi import Depends
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app import worker
from app.core.exceptions import HTTP403ForbiddenException
from app.db.session import get_db
from app.enums.sample import Status
from app.enums.tusd import HookName
from app.schemas.http_errors import HTTP403ForbiddenContent, HTTP403ForbiddenResponse
from app.schemas.sample import SampleDbCreate, SampleDbRead, SampleDbUpdate
from app.schemas.tusd import HookBody
from app.services.base import BaseService
from app.services.sample import SampleService, get_sample_service

logger: logging.Logger = logging.getLogger(__name__)


class TusdService(BaseService):
    def __init__(self, db: AsyncSession, sample_svc: SampleService) -> None:
        super().__init__(db)
        self.sample_svc: SampleService = sample_svc

    async def handle_notification(self, hook_body: HookBody, hook_name: HookName):
        upload_id = hook_body.upload.metadata["upload_id"]

        if hook_name == HookName.PRE_CREATE:
            try:
                await self.sample_svc.create(
                    sample=SampleDbCreate(upload_id=upload_id, status=Status.UPLOADING)
                )
            except exc.IntegrityError:
                logger.error(f"Duplicate upload id [{upload_id=}]")
                raise HTTP403ForbiddenException(
                    response=HTTP403ForbiddenResponse(
                        content=HTTP403ForbiddenContent(
                            msg=f"Duplicate upload id [{upload_id=}]"
                        )
                    )
                )

        elif hook_name == HookName.POST_FINISH:
            key: str = hook_body.upload.storage.key  # type: ignore
            sample_db_read: SampleDbRead = await self.sample_svc.update_by_upload_id(
                upload_id=upload_id, sample_db_update=SampleDbUpdate(file_name=key)
            )

            # run in the main thread
            # await self.sample_svc.process(sample_id=sample_db_read.id)

            # run in a separate process
            worker.process_sample(sample_id=sample_db_read.id)


# Facade #############################


async def create_service(
    db: AsyncSession,
    sample_svc: SampleService,
) -> TusdService:
    tusd_svc: TusdService = TusdService(db, sample_svc)
    return tusd_svc


# Injectable Dependencies ############


async def get_tusd_service(
    db: AsyncSession = Depends(get_db),
    sample_svc: SampleService = Depends(get_sample_service),
) -> TusdService:
    tusd_svc: TusdService = await create_service(db, sample_svc)
    return tusd_svc
