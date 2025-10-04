"""
Professional Medical RAG API using FastAPI
Provides medical question answering with hybrid search and metrics tracking
"""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.database import database as db
from src.core.rag import rag
from src.services.s3_service import is_s3_available, upload_logs_to_s3


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Medical question to answer")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")


class FeedbackRequest(BaseModel):
    conversation_id: str = Field(..., description="Conversation ID")
    feedback: int = Field(
        ..., ge=-1, le=1, description="Feedback: 1 (positive), -1 (negative)"
    )


class QuestionResponse(BaseModel):
    conversation_id: str
    question: str
    answer: str
    response_time: float
    relevance: str
    total_cost: float
    search_results_count: int


class FeedbackResponse(BaseModel):
    message: str
    conversation_id: str


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Medical RAG API starting up...")
    yield
    # Shutdown
    print("Medical RAG API shutting down...")


# FastAPI app
app = FastAPI(
    title="Medical RAG Assistant API",
    description="Professional medical question answering using Retrieval-Augmented Generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="medical-rag-api",
        timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/search")
async def search_only(request: Dict[str, str]):
    """
    Test search functionality without OpenAI
    """
    try:
        from rag import search

        question = request.get("question", "")
        results = search(question, top_k=3)
        return {"question": question, "results_count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/question", response_model=QuestionResponse)
async def handle_question(request: QuestionRequest, background_tasks: BackgroundTasks):
    """
    Process medical question and return RAG-generated answer
    """
    start_time = datetime.utcnow()
    conversation_id = str(uuid.uuid4())

    try:
        # Call RAG function
        answer_data = rag(request.question, model=request.model)

        # Prepare response
        response = QuestionResponse(
            conversation_id=conversation_id,
            question=request.question,
            answer=answer_data["answer"],
            response_time=answer_data["response_time"],
            relevance=answer_data["relevance"],
            total_cost=answer_data["total_cost"],
            search_results_count=answer_data["search_results_count"],
        )

        # Save to database in background
        background_tasks.add_task(
            save_conversation_async, conversation_id, request.question, answer_data
        )

        # Log API call to S3
        if os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true":
            background_tasks.add_task(
                log_api_call_to_s3,
                "question",
                conversation_id,
                request.question,
                response.answer,
                start_time,
                datetime.utcnow(),
                "success",
            )

        return response

    except Exception as e:
        # Log API error to S3
        if os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true":
            background_tasks.add_task(
                log_api_call_to_s3,
                "question",
                conversation_id,
                request.question,
                None,
                start_time,
                datetime.utcnow(),
                "error",
                str(e),
            )
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )


@app.post("/feedback", response_model=FeedbackResponse)
async def handle_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Submit feedback for a conversation
    """
    start_time = datetime.utcnow()

    try:
        # Save feedback in background
        background_tasks.add_task(
            save_feedback_async, request.conversation_id, request.feedback
        )

        # Log feedback API call to S3
        if os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true":
            background_tasks.add_task(
                log_api_call_to_s3,
                "feedback",
                request.conversation_id,
                f"feedback: {request.feedback}",
                "feedback_saved",
                start_time,
                datetime.utcnow(),
                "success",
            )

        return FeedbackResponse(
            message=f"Feedback received for conversation {request.conversation_id}",
            conversation_id=request.conversation_id,
        )

    except Exception as e:
        # Log feedback error to S3
        if os.getenv("ENABLE_S3_LOGGING", "false").lower() == "true":
            background_tasks.add_task(
                log_api_call_to_s3,
                "feedback",
                request.conversation_id,
                f"feedback: {request.feedback}",
                None,
                start_time,
                datetime.utcnow(),
                "error",
                str(e),
            )
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """
    Get system metrics for monitoring
    """
    try:
        # Get metrics from database
        metrics = await get_system_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metrics: {str(e)}"
        )


# Background task functions
async def save_conversation_async(
    conversation_id: str, question: str, answer_data: Dict
):
    """Save conversation to database asynchronously"""
    try:
        db.save_conversation(
            conversation_id=conversation_id, question=question, answer_data=answer_data
        )
    except Exception as e:
        print(f"Error saving conversation {conversation_id}: {e}")


async def save_feedback_async(conversation_id: str, feedback: int):
    """Save feedback to database asynchronously"""
    try:
        db.save_feedback(conversation_id=conversation_id, feedback=feedback)
    except Exception as e:
        print(f"Error saving feedback for {conversation_id}: {e}")


async def get_system_metrics() -> Dict:
    """Get system metrics from database"""
    try:
        return db.get_metrics()
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return {"error": "Unable to retrieve metrics"}


async def log_api_call_to_s3(
    endpoint: str,
    conversation_id: str,
    request_data: str,
    response_data: Optional[str],
    start_time: datetime,
    end_time: datetime,
    status: str,
    error: Optional[str] = None,
):
    """Log API call details to S3"""
    try:
        if is_s3_available():
            log_data = {
                "endpoint": endpoint,
                "conversation_id": conversation_id,
                "request_data": request_data,
                "response_data": response_data,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "status": status,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }

            upload_logs_to_s3([log_data], f"api_{endpoint}")

    except Exception as e:
        print(f"Error logging API call to S3: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
