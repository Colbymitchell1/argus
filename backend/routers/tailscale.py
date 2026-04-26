from fastapi import APIRouter

from models.schemas import TailscaleStatusResponse, TailscaleNode
from services.tailscale_service import get_status, parse_node

router = APIRouter()


@router.get("/status", response_model=TailscaleStatusResponse)
async def get_tailscale_status():
    """Return current tailnet state — self node plus all peers."""
    available, data, error = await get_status()
    if not available or not data:
        return TailscaleStatusResponse(available=False, error=error)

    self_raw = data.get("Self") or {}
    self_node = TailscaleNode(**parse_node(self_raw, is_self=True)) if self_raw else None

    peers = [
        TailscaleNode(**parse_node(p, is_self=False))
        for p in (data.get("Peer") or {}).values()
    ]

    online_count = sum(1 for p in peers if p.online) + (1 if self_node and self_node.online else 0)
    total_count = len(peers) + (1 if self_node else 0)

    return TailscaleStatusResponse(
        available=True,
        backend_state=data.get("BackendState"),
        self_node=self_node,
        peers=peers,
        online_count=online_count,
        total_count=total_count,
    )
