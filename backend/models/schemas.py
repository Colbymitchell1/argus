from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Network ───────────────────────────────────────────────────────

class DeviceStatus(BaseModel):
    name: str
    ip: str
    mac: Optional[str] = None
    icon: str
    description: str
    online: bool
    latency_ms: Optional[float] = None
    checked_at: datetime


class NetworkStatusResponse(BaseModel):
    devices: List[DeviceStatus]
    online_count: int
    total_count: int


# ── Wake-on-LAN ───────────────────────────────────────────────────

class WolRequest(BaseModel):
    device_name: str


class WolResponse(BaseModel):
    success: bool
    device_name: str
    mac: str
    message: str


# ── Ollama ────────────────────────────────────────────────────────

class OllamaStatusResponse(BaseModel):
    online: bool
    host: str
    models: Optional[List[str]] = None
    message: str


class OllamaChatRequest(BaseModel):
    model: str
    prompt: str
    system: Optional[str] = "You are ARGUS, a helpful infrastructure assistant."


class OllamaChatResponse(BaseModel):
    model: str
    response: str
    done: bool


# ── System ────────────────────────────────────────────────────────

class SystemInfoResponse(BaseModel):
    app_name: str
    version: str
    uptime_seconds: float
    gateway_ip: str
    subnet: str


# ── Service health ────────────────────────────────────────────────

class ServiceStatus(BaseModel):
    name: str
    kind: str
    url: str
    subdomain: Optional[str] = None
    icon: str
    description: str
    online: bool
    response_ms: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    host_device: Optional[str] = None
    checked_at: datetime


class ServicesResponse(BaseModel):
    services: List[ServiceStatus]
    online_count: int
    total_count: int


# ── Tailscale ─────────────────────────────────────────────────────

class TailscaleNode(BaseModel):
    name: str
    hostname: str
    tailscale_ip: str
    online: bool
    os: Optional[str] = None
    last_seen: Optional[str] = None
    is_self: bool = False


class TailscaleStatusResponse(BaseModel):
    available: bool
    backend_state: Optional[str] = None
    self_node: Optional[TailscaleNode] = None
    peers: List[TailscaleNode] = Field(default_factory=list)
    online_count: int = 0
    total_count: int = 0
    error: Optional[str] = None


# ── Training capture ──────────────────────────────────────────────

class TrainingCaptureRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)
    system: Optional[str] = None
    model: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    rating: Optional[int] = Field(None, ge=1, le=5)
    source: Optional[str] = None       # 'kyra' | 'argus-ui' | 'manual'
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TrainingCaptureResponse(BaseModel):
    saved: bool
    captured_at: datetime
    total_records: int
    path: str


class TrainingStatsResponse(BaseModel):
    total_records: int
    path: str
    size_bytes: int
    last_capture: Optional[datetime] = None
