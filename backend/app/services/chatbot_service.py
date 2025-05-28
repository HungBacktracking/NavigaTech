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


# Helper function to adapt different types of generators to async generator
async def async_generator_adapter(generator):
    """
    Adapts any type of generator (sync or async) to be used with async for.
    """
    # If it's already an async generator
    if hasattr(generator, '__aiter__'):
        try:
            async for item in generator:
                yield item
        except Exception as e:
            print(f"Error in async generator: {e}")
            raise
    else:
        # If it's a regular generator or iterable
        try:
            if hasattr(generator, '__iter__'):
                for item in generator:
                    yield item
            else:
                # If it's not iterable at all, yield it as a single item
                yield generator
        except TypeError as e:
            # If it's not iterable at all, yield it as a single item
            yield generator
        except Exception as e:
            print(f"Error in sync generator: {e}")
            raise


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
        try:
            self.verify_user(user_id)
            sid = await self.chatbot_repo.create_session(user_id, title)

            return SessionResponse(
                id=sid,
                title=title
            )
        except Exception as e:
            print(f"Error creating session: {e}")
            raise CustomError.INTERNAL_SERVER_ERROR.as_exception()

    async def list_sessions(self, user_id: str) -> list[SessionResponse]:
        try:
            self.verify_user(user_id)
            docs = await self.chatbot_repo.list_sessions(user_id)

            return [
                SessionResponse(
                    id=str(doc["_id"]),
                    title=doc["title"]
                )
                for doc in docs
            ]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            raise CustomError.INTERNAL_SERVER_ERROR.as_exception()

    async def generate_message_stream(self, session_id: str, message: str, user_id: str):
        try:
            self.verify_user(user_id)

            session = await self.chatbot_repo.find_session(session_id, user_id)
            if not session:
                yield f"ERROR: Session not found or doesn't belong to the user"
                return

            user_detail = self.user_service.get_detail_by_id(user_id)
            resume_text = self.resume_converter.process(user_detail.model_dump())
            history = await self.get_messages(user_id, session_id)
            history = [message.model_dump() for message in history]

            self.chat_engine.compose(resume_text, history, session_id)

            await self.post_message(user_id, session_id, "user", message)

            full_response = ""
            try:
                generator = self.chat_engine.stream_chat(message)
                if hasattr(generator, '__await__'):
                    generator = await generator

                async for chunk in async_generator_adapter(generator):
                    if chunk:
                        # Clean chunk from error prefixes if they exist
                        if not chunk.startswith("ERROR:"):
                            full_response += chunk
                            yield chunk
                        else:
                            # Pass error messages through but don't save them
                            yield chunk
                            return
            except Exception as e:
                error_msg = f"ERROR: Failed to generate response - {str(e)}"
                print(error_msg)
                yield error_msg
                return

            if full_response:
                try:
                    await self.post_message(user_id, session_id, "assistant", full_response)
                except Exception as e:
                    print(f"Error saving assistant message: {e}")
                    # Don't yield error to user since response was already sent
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print(error_msg)
            yield error_msg

    async def post_message(self, user_id: str, session_id: str, role: str, content: str) -> MessageResponse:
        self.verify_user(user_id)

        session = await self.chatbot_repo.find_session(session_id, user_id)
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
        try:
            self.verify_user(user_id)

            session = await self.chatbot_repo.find_session(session_id, user_id)
            if not session:
                raise CustomError.NOT_FOUND.as_exception()

            docs = await self.chatbot_repo.get_messages(session_id)

            return [
                MessageResponse(
                    id=str(doc["_id"]),
                    role=doc.get("role", "user"),
                    content=doc.get("content", ""),
                    timestamp=doc.get("timestamp")
                )
                for doc in docs
            ]
        except Exception as e:
            print(f"Error getting messages: {e}")
            raise CustomError.INTERNAL_SERVER_ERROR.as_exception()

