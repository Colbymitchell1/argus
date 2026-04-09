from pydantic_settings import BaseSettings
from typing import List
import os


class Device:
    def __init__(self, name: str, ip: str, mac: str = None, icon: str = "server", description: str = ""):
        self.name = name
        self.ip = ip
        self.mac = mac
        self.icon = icon
        self.description = description


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ARGUS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Network
    SUBNET: str = "192.168.50.0/24"
    GATEWAY_IP: str = "192.168.50.1"

    # Ollama
    OLLAMA_HOST: str = "192.168.50.56"
    OLLAMA_PORT: int = 11434

    # Security
    API_KEY: str = "change-this-before-deploy"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# ── Device Registry ────────────────────────────────────────────────
# Add/remove devices here. This is the single source of truth.
DEVICES: List[Device] = [
    Device(
        name="Router",
        ip="192.168.50.1",
        icon="router",
        description="ASUS GT-BE98 Pro — VPN Server / Network Core",
    ),
    Device(
        name="Legion",
        ip="192.168.50.56",
        mac="A8:3B:76:2A:37:89",
        icon="gpu",
        description="Lenovo Legion — Ollama AI Inference",
    ),
    Device(
        name="Beelink",
        ip="192.168.50.100",   # Update once Beelink is on network
        icon="nas",
        description="Beelink ME Mini — TrueNAS / Immich / ARGUS Backend",
    ),
]

# Quick lookup by name
DEVICE_MAP = {d.name: d for d in DEVICES}
