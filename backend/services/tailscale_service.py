"""Tailscale tailnet status via the local CLI.

Calls `tailscale status --json` and normalizes the output. Requires the
Tailscale CLI to be installed and the daemon running on the Argus host.

On macOS via the Tailscale.app cask, the binary lives at:
    /Applications/Tailscale.app/Contents/MacOS/Tailscale
We resolve via PATH first, then fall back to that absolute path.
"""
import asyncio
import json
import shutil
import os
from typing import Tuple, Optional, Dict, Any


_TAILSCALE_FALLBACK_PATHS = [
    "/Applications/Tailscale.app/Contents/MacOS/Tailscale",
    "/usr/local/bin/tailscale",
    "/opt/homebrew/bin/tailscale",
    "/usr/bin/tailscale",
]

# Go's zero-value timestamp. Tailscale returns this for currently-connected
# peers because there's no "last seen" — they're online right now.
_GO_ZERO_TIMESTAMP = "0001-01-01T00:00:00Z"


def _find_tailscale_binary() -> Optional[str]:
    binary = shutil.which("tailscale")
    if binary:
        return binary
    for path in _TAILSCALE_FALLBACK_PATHS:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


async def get_status() -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Run `tailscale status --json` and return (available, parsed_json, error)."""
    binary = _find_tailscale_binary()
    if not binary:
        return False, None, "tailscale binary not found on PATH"

    try:
        proc = await asyncio.create_subprocess_exec(
            binary, "status", "--json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        if proc.returncode != 0:
            return False, None, stderr.decode().strip() or f"exit {proc.returncode}"
        return True, json.loads(stdout.decode()), None
    except asyncio.TimeoutError:
        return False, None, "tailscale status timed out"
    except Exception as e:
        return False, None, f"{e.__class__.__name__}: {e}"


def _normalize_timestamp(raw: Optional[str]) -> Optional[str]:
    """Return None for Go zero-value timestamps (currently-online peers)."""
    if not raw or raw.startswith("0001-01-01"):
        return None
    return raw


def parse_node(raw: Dict[str, Any], is_self: bool = False) -> Dict[str, Any]:
    """Normalize a Tailscale peer/self block into our schema shape."""
    ips = raw.get("TailscaleIPs") or []
    return {
        "name": raw.get("HostName") or raw.get("DNSName", "").split(".")[0],
        "hostname": raw.get("DNSName", ""),
        "tailscale_ip": ips[0] if ips else "",
        "online": bool(raw.get("Online")),
        "os": raw.get("OS"),
        "last_seen": _normalize_timestamp(raw.get("LastSeen")),
        "is_self": is_self,
    }
