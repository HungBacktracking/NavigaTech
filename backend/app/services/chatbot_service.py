from uuid import UUID
from bson import ObjectId

from app.chatbot.chat_engine import ChatEngine
from app.exceptions.custom_error import CustomError
from app.repository import UserRepository
from app.repository.chatbot_repository import ChatbotRepository
from app.resume_building.resume_convert import ResumeConverter
from app.schema.chat_schema import SessionResponse, MessageResponse
from app.services import UserService
from app.services.base_service import BaseService


class ChatbotService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
        chatbot_repository: ChatbotRepository,
        user_service: UserService,
        chat_engine: ChatEngine
    ):
        self.chatbot_repo = chatbot_repository
        self.user_repo = user_repository
        self.user_service = user_service
        self.resume_converter = ResumeConverter(data={})
        self.chat_engine = chat_engine
        super().__init__(user_repository)

    def verify_user(self, user_id: str):
        user = self.user_repo.find_by_id(UUID(user_id))
        if not user:
            raise CustomError.NOT_FOUND.as_exception()

    async def create_session(self, user_id: str, title: str) -> SessionResponse:
        self.verify_user(user_id)
        sid = await self.chatbot_repo.create_session(user_id, title)

        return SessionResponse(
            id=sid,
            title=title
        )

    async def list_sessions(self, user_id: str) -> list[SessionResponse]:
        self.verify_user(user_id)
        docs = await self.chatbot_repo.list_sessions(user_id)

        return [
            SessionResponse(
                id=str(doc["_id"]),
                title=doc["title"]
            )
            for doc in docs
        ]

    async def generate_message(self, session_id: str, message: str, user_id: str):
        self.verify_user(user_id)

        user_detail = self.user_service.get_detail_by_id(user_id)
        resume_text = self.resume_converter.process(user_detail.model_dump())
        history = await self.get_messages(user_id, session_id)
        history = [message.model_dump() for message in history]

        self.chat_engine.compose(resume_text, history, session_id)
        return self.chat_engine.chat(message)

    async def post_message(self, user_id: str, session_id: str, role: str, content: str) -> MessageResponse:
        self.verify_user(user_id)

        session = await self.chatbot_repo.sessions.find_one({
            "_id": ObjectId(session_id)},
            {"user_id": user_id
        })
        if not session:
            raise CustomError.NOT_FOUND.as_exception()

        mid, role, content, ts = await self.chatbot_repo.post_message(session_id, role, content)


        return MessageResponse(
            id=mid,
            role=role,
            content=content,
            timestamp=ts,
        )

    async def get_messages(self, user_id: str, session_id: str) -> list[MessageResponse]:
        self.verify_user(user_id)
        session = await self.chatbot_repo.sessions.find_one({
            "_id": ObjectId(session_id),
            "user_id": user_id
        })
        if not session:
            raise CustomError.NOT_FOUND.as_exception()

        docs = await self.chatbot_repo.get_messages(session_id)

        return [
            MessageResponse(
                id=str(doc["_id"]),
                role=doc["role"],
                content=doc["content"],
                timestamp=doc["timestamp"]
            )
            for doc in docs
        ]

