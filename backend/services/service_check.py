"""HTTP health checks against registered services.

Distinct from ping_service: ICMP only proves a host is up. This proves the
actual service is responding on its port with the expected status code.
"""
import asyncio
import time
from typing import List, Tuple, Optional
import httpx

from config import Service


async def check_service(service: Service) -> Tuple[bool, Optional[float], Optional[int], Optional[str]]:
    """Probe a single service. Returns (online, response_ms, status_code, error)."""
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=service.timeout_seconds, follow_redirects=False) as client:
            r = await client.get(service.url)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
            online = r.status_code == service.expected_status
            return online, elapsed_ms, r.status_code, None
    except httpx.TimeoutException:
        return False, None, None, "timeout"
    except httpx.ConnectError as e:
        return False, None, None, f"connect: {e.__class__.__name__}"
    except Exception as e:
        return False, None, None, f"{e.__class__.__name__}: {str(e)[:80]}"


async def check_all(services: List[Service]):
    """Probe all services concurrently."""
    results = await asyncio.gather(
        *(check_service(s) for s in services),
        return_exceptions=False,
    )
    return list(zip(services, results))
