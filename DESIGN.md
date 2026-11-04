# PlotPermit – System Design

## 1. Project Overview

PlotPermit is a GenAI-powered application that uses Google's Gemini API to generate answers to user questions related to land and plot permits.

The application is built using FastAPI and Python. It provides API endpoints for health checking, AI-based response generation, and token usage monitoring.

## 2. Technology Stack

- **Programming Language:** Python 3.12
- **Backend Framework:** FastAPI
- **AI Model Provider:** Google Gemini
- **AI SDK:** google-genai
- **Data Validation:** Pydantic
- **Server:** Uvicorn
- **Containerization:** Docker

## 3. System Architecture

The application follows a simple API-based architecture.

1. The user sends a request through the API.
2. FastAPI receives and validates the request.
3. The Gemini service sends the prompt to the primary Gemini model.
4. If the primary model fails, the fallback model is attempted.
5. The generated response and usage information are returned.

### Architecture Flow

User → FastAPI → Gemini Service → Primary Gemini Model

If the primary model fails:

Gemini Service → Fallback Gemini Model

The response is returned to the user through FastAPI.

## 4. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Checks application health |
| POST | /generate | Generates an AI response |
| GET | /usage | Returns token usage and estimated cost |

### 4.1 Health Check

**Endpoint:** GET /health

Checks whether the application is running.

Sample response:

```json
{
  "status": "ok",
  "app": "PlotPermit",
  "environment": "local"
}
```

### 4.2 Generate Response

**Endpoint:** POST /generate

Accepts a user prompt and generates an answer using Gemini.

Sample request:

```json
{
  "prompt": "Explain land zoning in simple words."
}
```

Sample response:

```json
{
  "answer": "Land zoning is a way of dividing land into different areas based on permitted uses.",
  "model_used": "Gemini with fallback"
}
```

### 4.3 Usage Monitoring

**Endpoint:** GET /usage

Tracks API usage information.

The response includes:

- Total requests
- Input tokens
- Output tokens
- Total tokens reported by the API
- Estimated API cost in USD

Sample response:

```json
{
  "total_requests": 1,
  "input_tokens": 11,
  "output_tokens": 416,
  "total_tokens": 1215,
  "estimated_cost_usd": 0.00156825
}
```

Note: Usage statistics are maintained in application memory and reset when the application restarts.

## 5. Data Models

### GenerateRequest

| Field | Type | Description |
|---|---|---|
| prompt | String | User question sent to Gemini |

Validation:
- Prompt is required.
- Prompt must contain at least one character.

### GenerateResponse

| Field | Type | Description |
|---|---|---|
| answer | String | Generated AI response |
| model_used | String | Model information |

## 6. Configuration

Application configuration is maintained in `app/config.py`.

Environment variables:

- GEMINI_API_KEY – API key for Gemini authentication.
- GEMINI_MODEL – Primary Gemini model.
- FALLBACK_MODEL – Backup Gemini model.

Sensitive API keys are stored in the `.env` file and should not be committed to GitHub.

## 7. Error Handling

The application uses FastAPI HTTPException to handle generation failures.

- If Gemini generation fails, the service attempts the fallback model.
- If both attempts fail, the API returns an HTTP 500 error.
- Invalid request data is handled through Pydantic validation.

## 8. Security and Reliability

- API keys are stored using environment variables.
- Docker runs the application using a non-root user.
- A Docker HEALTHCHECK monitors the application health endpoint.
- A fallback model improves availability when the primary model fails.

## 9. Current Limitations

- Usage statistics are stored in memory.
- Usage information resets when the application restarts.
- A persistent database is not currently implemented.
- Authentication and user-specific access control are not currently implemented.

## 10. Future Enhancements

- Integrate a database for persistent storage.
- Add user authentication.
- Improve usage and cost monitoring.
- Add a frontend interface.
- Expand the land and plot permit knowledge base.