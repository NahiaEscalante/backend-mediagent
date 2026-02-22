from fastapi import APIRouter, Depends

from dependencies import get_current_user
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import obtener_respuesta_agente

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: dict = Depends(get_current_user)):
    """Recibe el mensaje del usuario y devuelve la respuesta del agente y si requiere revisión."""
    reply, requires_review = obtener_respuesta_agente(
        body.message,
        conversation_id=body.conversation_id,
        contexto_usuario=user,
    )
    return ChatResponse(reply=reply, requires_review=requires_review)
