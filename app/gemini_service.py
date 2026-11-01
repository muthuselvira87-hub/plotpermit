
from google import genai

from app.config import get_settings

usage_stats = {
    "total_requests": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0,
    "estimated_cost_usd": 0.0
}


def record_usage(response):
    metadata = response.usage_metadata

    input_tokens = metadata.prompt_token_count or 0
    output_tokens = metadata.candidates_token_count or 0
    total_tokens = metadata.total_token_count or 0

    usage_stats["total_requests"] += 1
    usage_stats["input_tokens"] += input_tokens
    usage_stats["output_tokens"] += output_tokens
    usage_stats["total_tokens"] += total_tokens

    # Estimated standard pricing in USD per million tokens
    cost = (
        input_tokens * 0.75 / 1_000_000
        + output_tokens * 3.75 / 1_000_000
    )

    usage_stats["estimated_cost_usd"] += cost


def generate_response(prompt: str) -> str:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise ValueError("Gemini API key is missing")

    client = genai.Client(api_key=settings.gemini_api_key)

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt
        )

    except Exception:
        print("Primary model failed. Trying fallback model...")

        response = client.models.generate_content(
            model=settings.fallback_model,
            contents=prompt
        )

    record_usage(response)

    return response.text or ""
