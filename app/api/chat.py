""""""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from ..services.rag_service_groq import RAGServiceGroq

router = APIRouter(prefix="/chat", tags=["Chat"])

rag_service = RAGServiceGroq()

conversation_history = []


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question must not be empty")
        
        doc_filter = {"document_id": request.document_id} if request.document_id else None
        result = rag_service.query(request.question, document_filter=doc_filter)
        
        conversation_entry = {
            "question": request.question,
            "answer": result["answer"],
            "timestamp": datetime.now().isoformat(),
            "sources_count": len(result.get("sources", []))
        }
        conversation_history.append(conversation_entry)
        
        if len(conversation_history) > 100:
            conversation_history.pop(0)
        
        return ChatResponse(
            success=result["success"],
            answer=result["answer"],
            question=request.question,
            sources=result.get("sources", []),
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(
            success=False,
            answer=f"Error handling question: {str(e)}",
            question=request.question,
            sources=[],
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )


@router.get("/history")
async def get_conversation_history(limit: int = 20):
    try:
        recent_history = conversation_history[-limit:] if conversation_history else []
        
        return {
            "success": True,
            "history": recent_history,
            "total_count": len(conversation_history),
            "returned_count": len(recent_history)
        }
        
    except Exception as e:
        return {
            "success": False,
            "history": [],
            "error": f"Failed to get history: {str(e)}"
        }


@router.post("/search", response_model=SearchResponse)
async def search_similar_content(request: SearchRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query must not be empty")
        
        results = rag_service.search_similar(request.query, k=request.limit)
        
        return SearchResponse(
            success=True,
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return SearchResponse(
            success=False,
            results=[],
            query=request.query,
            total_results=0,
            error=f"Search error: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    try:
        feedback_entry = {
            "question": request.question,
            "answer": request.answer,
            "rating": request.rating,
            "comment": request.comment,
            "timestamp": datetime.now().isoformat()
        }
        print(f"Feedback: {feedback_entry}")
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted"
        )
        
    except Exception as e:
        return FeedbackResponse(
            success=False,
            message=f"Feedback failed: {str(e)}",
            error=str(e)
        )


@router.get("/suggestions")
async def get_question_suggestions():
    try:
        suggestions = [
            "What is the main content of the document?",
            "Summarize the key points.",
            "Any important data or statistics?",
            "What methods or techniques are mentioned?",
            "What should I pay attention to?",
        ]
        
        return {
            "success": True,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        return {
            "success": False,
            "suggestions": [],
            "error": f"Failed to get suggestions: {str(e)}"
        }


@router.delete("/history")
async def clear_conversation_history():
    try:
        global conversation_history
        conversation_history.clear()
        
        return {
            "success": True,
            "message": "History cleared"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to clear history: {str(e)}",
            "error": str(e)
        }
