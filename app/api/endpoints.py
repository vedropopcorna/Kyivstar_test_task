from fastapi import APIRouter, HTTPException
from app.api.models import APIRequest, APIResponse
from core.chatbot import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()

@router.post("/chat", response_model=APIResponse)
async def chat_endpoint(request: APIRequest):
    try:
        # Make sure this returns the exact APIResponse structure
        return chatbot_service.process_query(request)
    except Exception as e:
        # Add logging here to debug
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))