
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


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question about Tamil Nadu building rules"
    )


class SourceCitation(BaseModel):
    source: str
    page_number: int


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
