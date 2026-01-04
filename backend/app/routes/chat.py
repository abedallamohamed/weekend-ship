from fastapi import APIRouter, HTTPException, Request
from typing import List
from pydantic import BaseModel
from app.models.chat import MessageRequest, ConversationResponse
from app.services.message_service import message_service
from app.middleware.session import get_session_id

router = APIRouter(prefix="/api", tags=["chat"])


class UpdateTaskRequest(BaseModel):
    """Request to update task completion status"""
    time_block_index: int
    task_index: int
    completed: bool


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(request: Request):
    """Get all conversations for current session"""
    session_id = get_session_id(request)
    conversations = await message_service.get_conversations(user=session_id)
    return conversations


@router.post("/conversations", response_model=ConversationResponse)
async def send_message(message_data: MessageRequest, request: Request):
    """Process user message and generate bot response"""
    session_id = get_session_id(request)
    
    # Process user message and generate bot response
    conversation = await message_service.process_user_message(message_data, user=session_id)
    
    return ConversationResponse(
        id=conversation.id,
        user_message=conversation.user_message,
        bot_response=conversation.bot_response,
        project_plan=conversation.project_plan,
        timestamp=conversation.timestamp
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get a specific conversation by ID"""
    conversation = await message_service.get_conversation_by_id(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations")
async def clear_conversations(request: Request):
    """Clear all conversations for current session"""
    session_id = get_session_id(request)
    await message_service.clear_user_conversations(user=session_id)
    return {"message": "Conversations cleared successfully"}


@router.patch("/conversations/{conversation_id}/tasks")
async def update_task_status(conversation_id: str, update: UpdateTaskRequest, request: Request):
    """Update the completion status of a specific task"""
    session_id = get_session_id(request)
    
    success = await message_service.update_task_completion(
        conversation_id=conversation_id,
        user=session_id,
        time_block_index=update.time_block_index,
        task_index=update.task_index,
        completed=update.completed
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation or task not found")
    
    return {"message": "Task status updated successfully"}
