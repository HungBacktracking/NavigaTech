from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self, mongo_url: str, db_name: str):
        self.mongo_url = mongo_url
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        self.sessions_coll = self.db["sessions"]
        self.messages_coll = self.db["messages"]

    async def init_mongo(self) -> None:
        await self.sessions_coll.create_index(
            [("user_id", 1), ("updated_at", -1)],
            name="idx_user_updated"
        )

        await self.sessions_coll.create_index(
            "updated_at",
            expireAfterSeconds = 30 * 24 * 3600,
            name = "ttl_updated"
        )

        await self.messages_coll.create_index(
            [("session_id", 1), ("timestamp", 1)],
            name="idx_session_timestamp"
        )
