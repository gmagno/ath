import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.http_errors import HTTP401UnauthorizedContent, HTTP403ForbiddenContent
from app.schemas.sample import SampleReadListResponse
from app.services.sample import SampleService, get_sample_service

sample_router: APIRouter = APIRouter()
settings: Settings = get_settings()
logger: logging.Logger = logging.getLogger(__name__)


@sample_router.get(
    "/samples",
    response_model=SampleReadListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": HTTP401UnauthorizedContent,
            "description": "Not authenticated",
        },
        status.HTTP_403_FORBIDDEN: {
            "model": HTTP403ForbiddenContent,
            "description": "Not enough privileges",
        },
    },
)
async def list_samples(
    *,
    # auth_token_payload: TokenPayload = Depends(oauth2_token_payload),
    db: AsyncSession = Depends(get_db),
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(10, ge=1),
    upload_id: Optional[uuid.UUID] = None,
    sample_svc: SampleService = Depends(get_sample_service),
) -> SampleReadListResponse:
    """List samples."""
    sample_read_list_response: SampleReadListResponse = await sample_svc.list(
        skip=skip, limit=limit, upload_id=upload_id
    )
    return sample_read_list_response
