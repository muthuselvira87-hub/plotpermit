from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="The question or prompt sent to Gemini"
    )


class GenerateResponse(BaseModel):
    answer: str
    model_used: str