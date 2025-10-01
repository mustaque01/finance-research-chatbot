"""
Chat endpoint for processing financial research queries
"""

import asyncio
from typing import Dict, Any, AsyncGenerator
import json

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.simple_workflow import create_research_graph
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message/query")
    thread_id: str = Field(..., description="Thread ID for conversation context")
    user_id: str = Field(..., description="User ID")
    conversation_history: list = Field(default=[], description="Previous conversation messages")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class ChatResponse(BaseModel):
    """Chat response model"""
    content: str = Field(..., description="Generated response content")
    thinking_trace: Dict[str, Any] = Field(default={}, description="Agent reasoning trace")
    sources: list = Field(default=[], description="Source references")
    metadata: Dict[str, Any] = Field(default={}, description="Response metadata")


@router.post("/process", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return a complete response
    """
    try:
        logger.info("Processing chat request", 
                   thread_id=request.thread_id, 
                   user_id=request.user_id,
                   message_length=len(request.message))
        
        # Create the research graph
        graph = create_research_graph()
        
        # Prepare input for the graph
        graph_input = {
            "query": request.message,
            "thread_id": request.thread_id,
            "user_id": request.user_id,
            "conversation_history": request.conversation_history,
            "metadata": request.metadata,
            "research_depth": request.metadata.get("research_depth", "deep"),
        }
        
        # Execute the graph
        result = await graph.ainvoke(graph_input)
        
        # Extract response components
        response = ChatResponse(
            content=result.get("final_response", ""),
            thinking_trace=result.get("thinking_trace", {}),
            sources=result.get("sources", []),
            metadata={
                "processing_time": result.get("processing_time"),
                "nodes_executed": result.get("nodes_executed", []),
                "total_sources_found": len(result.get("sources", [])),
            }
        )
        
        logger.info("Chat request processed successfully",
                   thread_id=request.thread_id,
                   response_length=len(response.content),
                   sources_count=len(response.sources))
        
        return response
        
    except Exception as e:
        logger.error("Error processing chat request", 
                    error=str(e), 
                    thread_id=request.thread_id)
        raise HTTPException(status_code=500, detail=f"Failed to process request: {str(e)}")


@router.post("/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    """
    Stream a chat response with real-time updates
    """
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            logger.info("Starting streaming chat request",
                       thread_id=request.thread_id,
                       user_id=request.user_id)
            
            # Create the research graph
            graph = create_research_graph()
            
            # Prepare input for the graph
            graph_input = {
                "query": request.message,
                "thread_id": request.thread_id,
                "user_id": request.user_id,
                "conversation_history": request.conversation_history,
                "metadata": {**request.metadata, "streaming": True},
                "research_depth": request.metadata.get("research_depth", "deep"),
            }
            
            # Stream the execution
            async for event in graph.astream_events(graph_input, version="v1"):
                event_type = event.get("event")
                event_data = event.get("data", {})
                
                if event_type == "on_chat_model_stream":
                    # Stream tokens from LLM
                    if "chunk" in event_data:
                        chunk = event_data["chunk"]
                        if hasattr(chunk, "content") and chunk.content:
                            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                
                elif event_type == "on_tool_start":
                    # Tool execution started
                    tool_name = event_data.get("name", "unknown")
                    yield f"data: {json.dumps({'type': 'thinking', 'data': {'step': f'Using {tool_name}', 'status': 'started'}})}\n\n"
                
                elif event_type == "on_tool_end":
                    # Tool execution completed
                    tool_name = event_data.get("name", "unknown")
                    output = event_data.get("output", {})
                    
                    if tool_name in ["web_search", "scraper"]:
                        # Send sources as they're found
                        sources = output.get("sources", [])
                        for source in sources:
                            yield f"data: {json.dumps({'type': 'source', 'data': source})}\n\n"
                    
                    yield f"data: {json.dumps({'type': 'thinking', 'data': {'step': f'Completed {tool_name}', 'status': 'completed'}})}\n\n"
                
                elif event_type == "on_chain_end":
                    # Final result
                    result = event_data.get("output", {})
                    if "final_response" in result:
                        yield f"data: {json.dumps({'type': 'complete', 'data': result})}\n\n"
                        break
                
                # Add small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            logger.info("Streaming chat request completed",
                       thread_id=request.thread_id)
            
        except Exception as e:
            logger.error("Error in streaming chat",
                        error=str(e),
                        thread_id=request.thread_id)
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable proxy buffering
        }
    )