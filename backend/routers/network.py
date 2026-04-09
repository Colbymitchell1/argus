from fastapi import APIRouter
from datetime import datetime, timezone
from models.schemas import DeviceStatus, NetworkStatusResponse
from services.ping_service import ping_all
from config import DEVICES

router = APIRouter()


@router.get("/status", response_model=NetworkStatusResponse)
async def get_network_status():
    """Ping all registered devices and return their status."""
    results = await ping_all(DEVICES)

    statuses = []
    for device, (online, latency_ms) in results:
        statuses.append(DeviceStatus(
            name=device.name,
            ip=device.ip,
            mac=device.mac,
            icon=device.icon,
            description=device.description,
            online=online,
            latency_ms=latency_ms,
            checked_at=datetime.now(timezone.utc),
        ))

    online_count = sum(1 for s in statuses if s.online)

    return NetworkStatusResponse(
        devices=statuses,
        online_count=online_count,
        total_count=len(statuses),
    )


@router.get("/status/{device_name}", response_model=DeviceStatus)
async def get_device_status(device_name: str):
    """Ping a single device by name."""
    from fastapi import HTTPException
    from services.ping_service import ping_host
    from config import DEVICE_MAP

    device = DEVICE_MAP.get(device_name)
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")

    online, latency_ms = await ping_host(device.ip)

    return DeviceStatus(
        name=device.name,
        ip=device.ip,
        mac=device.mac,
        icon=device.icon,
        description=device.description,
        online=online,
        latency_ms=latency_ms,
        checked_at=datetime.now(timezone.utc),
    )
