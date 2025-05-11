from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.containers.chatbot_container import ChatbotContainer
from app.core.dependencies import get_current_user
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.chat_schema import SessionResponse, SessionCreate, MessageResponse, MessageCreate
from app.schema.user_schema import UserBasicResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["Chatbot"], dependencies=[Depends(JWTBearer())])

@router.get("/sessions", response_model=list[SessionResponse])
@inject
async def list_sessions(
    service: ChatbotService = Depends(Provide[ChatbotContainer.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return await service.list_sessions(str(current_user.id))

@router.post("/sessions", response_model=SessionResponse)
@inject
async def create_session(
    data: SessionCreate,
    service: ChatbotService = Depends(Provide[ChatbotContainer.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return await service.create_session(str(current_user.id), data.title)

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
@inject
async def post_message(
    session_id: str,
    data: MessageCreate,
    service: ChatbotService = Depends(Provide[ChatbotContainer.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return await service.post_message(str(current_user.id), session_id, data.role, data.content)

@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
@inject
async def get_messages(
    session_id: str,
    limit: int = 20,
    service: ChatbotService = Depends(Provide[ChatbotContainer.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return await service.get_messages(str(current_user.id), session_id, limit)



