from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.containers.chatbot_container import ChatbotContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.chat_schema import ChatRequest
from app.schema.user_schema import UserDetailResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["Chatbot"], dependencies=[Depends(JWTBearer())])


@router.get("/")
@inject
def get_chat_response(
    chat_request: ChatRequest,
    chatbot_service: ChatbotService = Depends(Provide[ChatbotContainer.chatbot_service]),
    current_user: UserDetailResponse = Depends(get_current_user)
): return StreamingResponse(chatbot_service.get_chat_response(chat_request, current_user.id))



