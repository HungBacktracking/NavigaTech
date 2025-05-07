from uuid import UUID

from app.schema.chat_schema import ChatRequest


class ChatbotService:
    def get_chat_response(self, chat_request: ChatRequest, user_id: UUID):
        pass