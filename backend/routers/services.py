from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from models.schemas import ServiceStatus, ServicesResponse
from services.service_check import check_all, check_service
from config import SERVICES, SERVICE_MAP

router = APIRouter()


def _to_status(service, result) -> ServiceStatus:
    online, response_ms, status_code, error = result
    return ServiceStatus(
        name=service.name,
        kind=service.kind,
        url=service.url,
        subdomain=service.subdomain,
        icon=service.icon,
        description=service.description,
        online=online,
        response_ms=response_ms,
        status_code=status_code,
        error=error,
        host_device=service.host_device,
        checked_at=datetime.now(timezone.utc),
    )


@router.get("/status", response_model=ServicesResponse)
async def get_services_status():
    """Probe every registered service and return health for each."""
    results = await check_all(SERVICES)
    statuses = [_to_status(svc, res) for svc, res in results]
    return ServicesResponse(
        services=statuses,
        online_count=sum(1 for s in statuses if s.online),
        total_count=len(statuses),
    )


@router.get("/status/{service_name}", response_model=ServiceStatus)
async def get_single_service(service_name: str):
    """Probe a single registered service by name."""
    svc = SERVICE_MAP.get(service_name)
    if not svc:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not registered")
    result = await check_service(svc)
    return _to_status(svc, result)
