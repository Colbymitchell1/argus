from fastapi import APIRouter, HTTPException
from models.schemas import OllamaStatusResponse, OllamaChatRequest, OllamaChatResponse
from services.ollama_service import check_ollama_status, chat
from config import settings

router = APIRouter()


@router.get("/status", response_model=OllamaStatusResponse)
async def get_ollama_status():
    """Check if Ollama is reachable on the Legion."""
    online, models = await check_ollama_status()

    return OllamaStatusResponse(
        online=online,
        host=f"{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}",
        models=models,
        message="Ollama online" if online else "Ollama unreachable — Legion may be asleep",
    )


@router.post("/chat", response_model=OllamaChatResponse)
async def ollama_chat(request: OllamaChatRequest):
    """Send a prompt to Ollama on the Legion."""
    online, _ = await check_ollama_status()
    if not online:
        raise HTTPException(
            status_code=503,
            detail="Ollama is unreachable. Try waking the Legion first via /api/wol/wake."
        )

    success, response = await chat(
        model=request.model,
        prompt=request.prompt,
        system=request.system,
    )

    if not success:
        raise HTTPException(status_code=500, detail=response)

    return OllamaChatResponse(
        model=request.model,
        response=response,
        done=True,
    )
