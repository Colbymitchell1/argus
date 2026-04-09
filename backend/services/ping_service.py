import asyncio
import time
import platform
import logging

logger = logging.getLogger("argus.ping")


async def ping_host(ip: str, timeout: float = 1.5) -> tuple[bool, float | None]:
    """
    Async ping a host. Returns (is_online, latency_ms).
    Works on Linux (Beelink) and macOS (MacBook dev).
    """
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(int(timeout)), ip]

    start = time.monotonic()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.wait_for(proc.wait(), timeout=timeout + 0.5)
        elapsed = (time.monotonic() - start) * 1000

        if proc.returncode == 0:
            return True, round(elapsed, 2)
        return False, None

    except (asyncio.TimeoutError, Exception) as e:
        logger.debug(f"Ping failed for {ip}: {e}")
        return False, None


async def ping_all(devices: list, timeout: float = 1.5) -> list[tuple]:
    """Ping all devices concurrently."""
    tasks = [ping_host(d.ip, timeout) for d in devices]
    results = await asyncio.gather(*tasks)
    return list(zip(devices, results))
