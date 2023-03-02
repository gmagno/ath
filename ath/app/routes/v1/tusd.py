import logging

from fastapi import APIRouter, Depends, Header, Request, Response, status

# from app.core.auth import oauth2_token_payload
from app.core.config import get_settings
from app.enums.tusd import HookName
from app.schemas.http_errors import HTTP401UnauthorizedContent, HTTP403ForbiddenContent
from app.schemas.tusd import HookBody
from app.services.tusd import TusdService, get_tusd_service

tusd_router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)


@tusd_router.post(
    "/tusd-webhook-notification",
    status_code=status.HTTP_204_NO_CONTENT,
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
async def tusd_webhook_notification(
    request: Request,
    hook_body: HookBody,
    hook_name: HookName = Header(),
    # auth_token_payload: TokenPayload = Depends(oauth2_token_payload),
    tusd_svc: TusdService = Depends(get_tusd_service),
):
    """Creates image upload notification."""
    await tusd_svc.handle_notification(hook_body=hook_body, hook_name=hook_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
