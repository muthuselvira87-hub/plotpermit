
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.schemas import GenerateRequest, GenerateResponse
from app.gemini_service import generate_response, usage_stats

app = FastAPI(title="PlotPermit", version="0.1.0")

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
        )


@app.get("/usage")
def get_usage() -> dict:
    return usage_stats
