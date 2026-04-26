from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Device:
    def __init__(self, name: str, ip: str, mac: str = None, icon: str = "server", description: str = ""):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.icon = icon
        self.description = description


class Service:
    """A networked service Argus monitors via HTTP health check."""
    def __init__(
        self,
        name: str,
        url: str,
        kind: str,                  # plex | immich | ollama | argus | caddy | generic
        icon: str = "server",
        description: str = "",
        subdomain: Optional[str] = None,
        expected_status: int = 200,
        timeout_seconds: float = 3.0,
        host_device: Optional[str] = None,   # cross-reference into Device registry
    ):
        self.name = name
        self.url = url
        self.kind = kind
        self.icon = icon
        self.description = description
        self.subdomain = subdomain
        self.expected_status = expected_status
        self.timeout_seconds = timeout_seconds
        self.host_device = host_device


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ARGUS"
    APP_VERSION: str = "1.1.0"
    DEBUG: bool = False

    # Network
    SUBNET: str = "192.168.50.0/24"
    GATEWAY_IP: str = "192.168.50.1"

    # Crucible — Tailscale MagicDNS so it works regardless of network
    OLLAMA_HOST: str = "crucible"
    OLLAMA_PORT: int = 11434

    # Training capture
    TRAINING_DATA_PATH: str = "/Users/Shared/server/config/argus/training/captures.jsonl"

    # Security
    API_KEY: str = "change-this-before-deploy"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


# ── Device Registry ─────────────────────────────────────────────────
# LAN-only ICMP ping targets. Devices that move between networks (laptops,
# phones) belong on the Tailscale endpoint, not here.
DEVICES: List[Device] = [
    Device(
        name="Aether",
        ip="192.168.50.1",
        icon="router",
        description="ASUS GT-BE98 Pro — Network Core",
    ),
    Device(
        name="Crucible",
        ip="192.168.50.71",
        mac="40:C2:BA:38:09:04",
        icon="gpu",
        description="Lenovo Legion (Ubuntu) — Kyra inference, GPU compute",
    ),
    Device(
        name="Hephaestus",
        ip="192.168.50.215",
        icon="server",
        description="Mac mini — ARGUS / Immich / Plex host",
    ),
    # Pithos (UGREEN NAS) gets added once it arrives on the network.
]

DEVICE_MAP = {d.name: d for d in DEVICES}


# ── Service Registry ────────────────────────────────────────────────
# Networked services Argus monitors. Drives the dashboard tiles.
# Use Tailscale MagicDNS or .local hostnames so URLs survive IP changes.
SERVICES: List[Service] = [
    Service(
        name="Argus",
        url="http://localhost:8000/health",
        kind="argus",
        icon="dashboard",
        description="This dashboard",
        subdomain="argus.mitchelldynamics.com",
        host_device="Hephaestus",
    ),
    Service(
        name="Immich",
        url="http://localhost:2283/api/server/ping",
        kind="immich",
        icon="photos",
        description="Self-hosted photo library",
        subdomain="photos.mitchelldynamics.com",
        host_device="Hephaestus",
    ),
    Service(
        name="Plex",
        url="http://localhost:32400/identity",
        kind="plex",
        icon="media",
        description="Media server (deferred until Pithos arrives)",
        host_device="Hephaestus",
    ),
    Service(
        name="Kyra",
        url=f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/tags",
        kind="ollama",
        icon="brain",
        description="Local LLM on Crucible",
        host_device="Crucible",
    ),
    Service(
        name="Caddy",
        url="http://localhost:2019/config/",
        kind="caddy",
        icon="proxy",
        description="Reverse proxy + TLS",
        host_device="Hephaestus",
    ),
]

SERVICE_MAP = {s.name: s for s in SERVICES}
