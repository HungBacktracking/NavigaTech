from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.containers.application_container import ApplicationContainer
from app.core.dependencies import get_current_user
from app.core.security import JWTBearer
from app.schema.chat_schema import SessionResponse, SessionCreate, MessageResponse, MessageCreate
from app.schema.user_schema import UserBasicResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter(prefix="/chat", tags=["Chatbot"], dependencies=[Depends(JWTBearer())])


@router.get("/sessions", response_model=list[SessionResponse])
@inject
async def list_sessions(
    service: ChatbotService = Depends(Provide[ApplicationContainer.services.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return await service.list_sessions(str(current_user.id))

@router.post("/sessions", response_model=SessionResponse)
@inject
async def create_session(
    data: SessionCreate,
    service: ChatbotService = Depends(Provide[ApplicationContainer.services.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    return await service.create_session(str(current_user.id), data.title)

@router.post("/sessions/{session_id}/generate-response")
@inject
async def generate_response(
    session_id: str,
    data: MessageCreate,
    service: ChatbotService = Depends(Provide[ApplicationContainer.services.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user)
):
    async def response_generator():
        try:
            yield "event: start\ndata: \n\n"
            
            async for chunk in service.generate_message_stream(session_id, data.content, str(current_user.id)):
                if chunk:
                    if not isinstance(chunk, str):
                        chunk = str(chunk)

                    formatted_chunk = chunk.replace("\n", "\\n")
                    yield f"event: message\ndata: {formatted_chunk}\n\n"

            yield "event: done\ndata: \n\n"
            
        except Exception as e:
            error_message = str(e)
            yield f"event: error\ndata: {error_message}\n\n"
            
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in Nginx
        }
    )

@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
@inject
async def get_messages(
    session_id: str,
    service: ChatbotService = Depends(Provide[ApplicationContainer.services.chatbot_service]),
    current_user: UserBasicResponse = Depends(get_current_user),
):
    return await service.get_messages(str(current_user.id), session_id)



