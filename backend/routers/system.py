from fastapi import APIRouter
from models.schemas import SystemInfoResponse
from config import settings
import time

router = APIRouter()

START_TIME = time.monotonic()


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info():
    """Return ARGUS system info and uptime."""
    return SystemInfoResponse(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        uptime_seconds=round(time.monotonic() - START_TIME, 2),
        gateway_ip=settings.GATEWAY_IP,
        subnet=settings.SUBNET,
    )
