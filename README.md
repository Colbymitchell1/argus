# ARGUS
### Autonomous Remote Gateway & Unified System

Personal infrastructure command dashboard. Monitor devices, wake sleeping hardware, 
and interface with local AI from anywhere in the world via encrypted VPN tunnel.

---

## Stack
- **Backend**: Python FastAPI
- **Frontend**: React (single-file, served separately)
- **Deployment**: Docker Compose on Beelink ME Mini (TrueNAS)
- **Access**: WireGuard VPN tunnel via ASUS GT-BE98 Pro
- **AI**: Ollama on Lenovo Legion RTX 4070

---

## Features
- Real-time device status (ping all home network devices)
- Wake-on-LAN (remotely wake the Legion)
- Ollama AI chat proxy (model selector + prompt interface)
- System uptime and network info

---

## Quick Start

```bash
# Clone
git clone https://github.com/Colbymitchell1/argus
cd argus

# Configure
cp backend/.env.example backend/.env
# Edit backend/.env with your values

# Run locally
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Or with Docker
docker compose up --build
```

## API Docs
Once running, visit: `http://localhost:8000/docs`

FastAPI auto-generates interactive API documentation.

---

## Architecture

```
[Field — Hotel/Base]
  MacBook / iPhone
       |
  Beryl AX Travel Router
       |
  WireGuard Tunnel
       |
[Home Network — 192.168.50.0/24]
  ASUS GT-BE98 Pro (VPN Server)
       |
  ┌────┴────┐
  │         │
Beelink   Legion
ME Mini   RTX 4070
TrueNAS   Ollama
Immich
ARGUS Backend
```

---

## Roadmap
- [x] Phase 1: FastAPI backend + device monitoring + WoL
- [ ] Phase 2: React dashboard frontend
- [ ] Phase 3: Immich + TrueNAS storage integration
- [ ] Phase 4: VPN tunnel status + Beryl AX integration
- [ ] Phase 5: Portfolio documentation + architecture diagrams
