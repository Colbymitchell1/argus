import httpx
import logging
from config import settings

logger = logging.getLogger("argus.ollama")

OLLAMA_BASE = f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"


async def check_ollama_status() -> tuple[bool, list[str] | None]:
    """Check if Ollama is reachable and return available models."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_BASE}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m["name"] for m in data.get("models", [])]
                return True, models
            return False, None
    except Exception as e:
        logger.debug(f"Ollama unreachable: {e}")
        return False, None


async def chat(model: str, prompt: str, system: str) -> tuple[bool, str]:
    """Send a prompt to Ollama and return the response."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OLLAMA_BASE}/api/generate", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return True, data.get("response", "")
            return False, f"Ollama returned {resp.status_code}"
    except Exception as e:
        logger.error(f"Ollama chat failed: {e}")
        return False, str(e)
