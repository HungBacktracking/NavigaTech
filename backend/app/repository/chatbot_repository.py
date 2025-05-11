import datetime
from datetime import datetime, timezone
from bson import ObjectId


class ChatbotRepository:
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
        self.sessions = mongo_db["sessions"]
        self.messages = mongo_db["messages"]


    async def create_session(self, user_id: str, title: str):
        now = datetime.now(timezone.utc)
        doc = {
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "is_active": True
        }
        res = await self.sessions.insert_one(doc)

        return str(res.inserted_id)

    async def list_sessions(self, user_id: str):
        cursor = self.sessions.find(
            {"user_id": user_id}
        ).sort("updated_at", -1)

        return await cursor.to_list(length=None)

    async def post_message(self, session_id: str, role: str, content: str):
        now = datetime.now(timezone.utc)
        msg = {
            "session_id": ObjectId(session_id),
            "role": role,
            "content": content,
            "timestamp": now
        }
        res = await self.messages.insert_one(msg)

        await self.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"updated_at": now}}
        )

        return str(res.inserted_id), role, content, now

    async def get_messages(self, session_id: str):
        cursor = self.messages.find(
            {"session_id": ObjectId(session_id)}
        ).sort("timestamp", -1)
        docs = [doc async for doc in cursor]

        return list(reversed(docs))
