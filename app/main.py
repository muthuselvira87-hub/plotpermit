
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.gemini_service import generate_response, usage_stats
from app.rag_service import generate_rag_response
from app.schemas import (
    GenerateRequest,
    GenerateResponse,
    AskRequest,
    AskResponse
)


app = FastAPI(title="PlotPermit", version="0.2.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    try:
        answer = generate_response(request.prompt)

        return GenerateResponse(
            answer=answer,
            model_used="Gemini with fallback"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM generation failed: {str(e)}"
        ) from e


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        result = generate_rag_response(request.question)

        return AskResponse(
            answer=result["answer"],
            sources=result["sources"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG processing failed: {str(e)}"
        ) from e


@app.get("/usage")
def get_usage() -> dict:
    return usage_stats
