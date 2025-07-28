from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
from datetime import datetime
import asyncio
from utils.vertex_service import VertexRAGService

app = FastAPI(
    title="RAG Chat API",
    description="FastAPI RAG system with chat history and summarization",
    version="1.0.0"
)

# Global service instance
rag_service = None

# In-memory session storage (use Redis in production)
chat_sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_count: int
    used_rag: bool
    context_used: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG service on startup"""
    global rag_service
    try:
        rag_service = VertexRAGService()
        print("✅ RAG service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG service: {e}")
        raise e


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Chat API",
        "rag_initialized": rag_service is not None,
        "active_sessions": len(chat_sessions)
    }


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Non-streaming chat endpoint"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")

    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = chat_sessions.get(session_id, {
        "messages": [],
        "message_count": 0,
        "summary": "",
        "created_at": datetime.now().isoformat()
    })

    try:
        # Get response from RAG service
        response, context_used = rag_service.chat_with_history(
            message=request.message,
            session_data=session,
            use_rag=request.use_rag
        )

        # Update session
        session["messages"].append({
            "user": request.message,
            "assistant": response,
            "timestamp": datetime.now().isoformat(),
            "used_rag": request.use_rag
        })
        session["message_count"] += 1
        session["last_updated"] = datetime.now().isoformat()

        # Store updated session
        chat_sessions[session_id] = session

        return ChatResponse(
            response=response,
            session_id=session_id,
            message_count=session["message_count"],
            used_rag=request.use_rag,
            context_used=context_used[:200] + "..." if context_used and len(context_used) > 200 else context_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streaming chat endpoint"""
    if not rag_service:
        raise HTTPException(status_code=500, detail="RAG service not initialized")

    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    session = chat_sessions.get(session_id, {
        "messages": [],
        "message_count": 0,
        "summary": "",
        "created_at": datetime.now().isoformat()
    })

    async def generate_stream():
        try:
            full_response = ""
            context_used = ""

            # Get streaming response
            for chunk, context in rag_service.chat_with_history_stream(
                    message=request.message,
                    session_data=session,
                    use_rag=request.use_rag
            ):
                if context and not context_used:
                    context_used = context

                full_response += chunk

                # Stream response as SSE format
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'session_id': session_id})}\n\n"

            # Update session after streaming is complete
            session["messages"].append({
                "user": request.message,
                "assistant": full_response,
                "timestamp": datetime.now().isoformat(),
                "used_rag": request.use_rag
            })
            session["message_count"] += 1
            session["last_updated"] = datetime.now().isoformat()

            # Store updated session
            chat_sessions[session_id] = session

            # Send final metadata
            yield f"data: {json.dumps({'type': 'metadata', 'session_id': session_id, 'message_count': session['message_count'], 'context_used': context_used[:200] + '...' if context_used and len(context_used) > 200 else context_used})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session history"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]
    return {
        "session_id": session_id,
        "message_count": session["message_count"],
        "summary": session.get("summary", ""),
        "messages": session["messages"][-10:],  # Return last 10 messages
        "created_at": session["created_at"],
        "last_updated": session.get("last_updated")
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del chat_sessions[session_id]
    return {"message": f"Session {session_id} deleted successfully"}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions"""
    sessions_info = []
    for session_id, session_data in chat_sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "message_count": session_data["message_count"],
            "created_at": session_data["created_at"],
            "last_updated": session_data.get("last_updated"),
            "has_summary": bool(session_data.get("summary"))
        })

    return {
        "total_sessions": len(sessions_info),
        "sessions": sessions_info
    }


@app.post("/sessions/{session_id}/summarize")
async def force_summarize_session(session_id: str):
    """Force summarization of a session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = chat_sessions[session_id]

    try:
        summary = rag_service.summarize_conversation(session["messages"])
        session["summary"] = summary
        session["last_updated"] = datetime.now().isoformat()

        return {
            "session_id": session_id,
            "summary": summary,
            "message_count": session["message_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing session: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rag_service": {
            "initialized": rag_service is not None,
            "rag_enabled": rag_service.is_rag_initialized() if rag_service else False,
            "model_initialized": rag_service.is_initialized() if rag_service else False
        },
        "sessions": {
            "active_count": len(chat_sessions),
            "total_messages": sum(session.get("message_count", 0) for session in chat_sessions.values())
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os

    # Cloud Run provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Always False for production
        log_level="info"
    )