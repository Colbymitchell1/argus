from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import network, wol, ollama, system
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("argus")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ARGUS online.")
    yield
    logger.info("ARGUS offline.")


app = FastAPI(
    title="ARGUS",
    description="Autonomous Remote Command — Personal Infrastructure Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this after VPN is confirmed working
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(wol.router, prefix="/api/wol", tags=["Wake-on-LAN"])
app.include_router(ollama.router, prefix="/api/ollama", tags=["Ollama"])
app.include_router(system.router, prefix="/api/system", tags=["System"])


@app.get("/")
async def root():
    return {"status": "online", "system": "ARGUS", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
