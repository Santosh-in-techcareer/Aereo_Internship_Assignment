import asyncio
import os
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Ensure Chat_bot directory is importable
chatbot_dir = Path(__file__).resolve().parent.parent.parent / "Chat_bot"
if str(chatbot_dir) not in sys.path:
    sys.path.insert(0, str(chatbot_dir))

from geospatial_chatbot import chat_with_geospatial_data
from ..database import get_db
from ..models import Feature, File

router = APIRouter(
    prefix="/api/files",
    tags=["Chatbot"],
)

# Demo-only in-memory conversation storage keyed by file_id:session_id
chat_sessions = defaultdict(lambda: deque(maxlen=12))
llm_semaphore = asyncio.Semaphore(5)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field("default", min_length=1, max_length=100)


@router.post("/{file_id}/chat/")
async def geospatial_chat(
    file_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    # 1. Fetch file record from DB
    file_record = db.query(File).filter(File.id == file_id).first()
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="Dataset or file not found.",
        )

    # 2. Fetch features from DB
    features = (
        db.query(Feature)
        .filter(Feature.file_id == file_id)
        .order_by(Feature.feature_index)
        .all()
    )

    if not features:
        raise HTTPException(
            status_code=422,
            detail="No measurements or features available for this dataset.",
        )

    # 3. Format measurements for context
    measurements = [
        {
            "feature_id": feature.id,
            "feature_index": feature.feature_index,
            "geometry_type": feature.geometry_type,
            "geometry_wkt": feature.geometry_wkt,
            "area": feature.area,
            "perimeter": feature.perimeter,
            "length": feature.length,
            "unit": feature.measurement_unit,
            "status": feature.measurement_status,
        }
        for feature in features
    ]

    # 4. Retrieve session history
    session_key = f"{file_id}:{request.session_id}"
    history = list(chat_sessions[session_key])

    # 5. Invoke LangChain + Groq assistant
    try:
        async with llm_semaphore:
            answer = await asyncio.to_thread(
                chat_with_geospatial_data,
                request.question,
                measurements,
                history,
            )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"The AI assistant could not generate a response: {str(exc)}",
        )

    # Save session turn
    from langchain_core.messages import HumanMessage, AIMessage
    chat_sessions[session_key].extend([
        HumanMessage(content=request.question),
        AIMessage(content=answer),
    ])

    return {
        "file_id": file_id,
        "session_id": request.session_id,
        "question": request.question,
        "answer": answer,
    }
