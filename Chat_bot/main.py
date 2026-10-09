import os
import asyncio
import logging
from collections import defaultdict, deque

import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage

try:
    from .geospatial_chatbot import chat_with_geospatial_data
except ImportError:
    from geospatial_chatbot import chat_with_geospatial_data


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="GeoSmart AI Chatbot",
    description="LangChain and Groq powered geospatial assistant",
    version="1.0.0",
)


GEOSPATIAL_API_URL = os.getenv(
    "GEOSPATIAL_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# Demo-only in-memory conversation storage.
# History disappears when the application restarts.
chat_sessions = defaultdict(lambda: deque(maxlen=12))

# Limit concurrent LLM requests in this simple implementation.
llm_semaphore = asyncio.Semaphore(5)


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
    )

    session_id: str = Field(
        min_length=1,
        max_length=100,
    )


@app.get("/")
def home():
    return {
        "message": "GeoSmart AI Chatbot is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/api/files/{file_id}/chat/")
async def geospatial_chat(
    file_id: str,
    request: ChatRequest,
):

    # 1. Fetch measurements from the existing GIS backend.
    measurements_url = (
        f"{GEOSPATIAL_API_URL}/api/files/"
        f"{file_id}/measurements/"
    )

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(measurements_url)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Dataset or measurements not found.",
                )

            response.raise_for_status()
            data = response.json()

    except HTTPException:
        raise

    except httpx.HTTPError:
        logger.exception("Could not retrieve GIS measurements")

        raise HTTPException(
            status_code=502,
            detail="Could not connect to the geospatial API.",
        )

    measurements = data.get("measurements")

    if not isinstance(measurements, list):
        raise HTTPException(
            status_code=502,
            detail="Unexpected measurements API response.",
        )

    if not measurements:
        raise HTTPException(
            status_code=422,
            detail="No measurements are available for this dataset.",
        )

    # 2. Retrieve the session's conversation history.
    session_key = f"{file_id}:{request.session_id}"
    history = list(chat_sessions[session_key])

    # 3. Call LangChain + Groq.
    try:
        async with llm_semaphore:
            answer = await asyncio.to_thread(
                chat_with_geospatial_data,
                request.question,
                measurements,
                history,
            )

    except Exception:
        logger.exception("LLM request failed")

        raise HTTPException(
            status_code=502,
            detail="The AI assistant could not generate a response.",
        )

    # 4. Save this conversation turn.
    chat_sessions[session_key].extend([
        HumanMessage(content=request.question),
        AIMessage(content=answer),
    ])

    # 5. Return the answer to the client.
    return {
        "file_id": file_id,
        "session_id": request.session_id,
        "question": request.question,
        "answer": answer,
    }