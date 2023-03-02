from fastapi import APIRouter

from .auth import auth_router
from .sample import sample_router
from .tusd import tusd_router

router_v1 = APIRouter()
router_v1.include_router(auth_router, prefix="/auth", tags=["auth"])
router_v1.include_router(sample_router, prefix="", tags=["sample"])
router_v1.include_router(tusd_router, prefix="", tags=["tusd"])
