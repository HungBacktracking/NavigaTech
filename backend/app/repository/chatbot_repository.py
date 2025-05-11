from contextlib import AbstractContextManager
import datetime
from datetime import datetime
from typing import Callable
from uuid import UUID
from sqlmodel import Session, select
from app.model.education import Education
from app.repository.base_repository import BaseRepository
from bson import ObjectId


class ChatbotRepository:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.sessions = mongo_client.sessions
        self.messages = mongo_client.messages


    async def create_session(self, user_id: str, title: str):
        now = datetime.now(datetime.UTC)
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

        return [doc async for doc in cursor]

    async def post_message(self, session_id: str, role: str, content: str):
        now = datetime.now(datetime.UTC)
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

    async def get_messages(self, session_id: str, limit: int):
        cursor = self.messages.find(
            {"session_id": ObjectId(session_id)}
        ).sort("timestamp", -1).limit(limit)
        docs = [doc async for doc in cursor]

        return list(reversed(docs))
