from fastapi import APIRouter, HTTPException
from models.schemas import WolRequest, WolResponse
from services.wol_service import send_magic_packet
from config import DEVICE_MAP

router = APIRouter()


@router.post("/wake", response_model=WolResponse)
async def wake_device(request: WolRequest):
    """Send a Wake-on-LAN magic packet to a registered device."""
    device = DEVICE_MAP.get(request.device_name)

    if not device:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{request.device_name}' not found in registry"
        )

    if not device.mac:
        raise HTTPException(
            status_code=400,
            detail=f"Device '{request.device_name}' has no MAC address registered"
        )

    success = send_magic_packet(device.mac)

    return WolResponse(
        success=success,
        device_name=device.name,
        mac=device.mac,
        message="Magic packet sent" if success else "Failed to send magic packet",
    )


@router.get("/devices")
async def list_wol_devices():
    """List all devices that have a MAC address registered (WoL capable)."""
    return [
        {"name": d.name, "mac": d.mac, "ip": d.ip}
        for d in DEVICE_MAP.values()
        if d.mac
    ]
