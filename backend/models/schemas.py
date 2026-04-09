from pydantic import BaseModel
from typing import Optional, List
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
