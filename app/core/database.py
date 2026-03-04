from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from app.config import get_settings

settings = get_settings()


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_db():
    db_instance.client = AsyncIOMotorClient(settings.mongo_uri)
    db_instance.db = db_instance.client[settings.mongo_db_name]
    await create_indexes()
    print(f"Connected to MongoDB: {settings.mongo_db_name}")


async def disconnect_db():
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed.")


async def get_db():
    return db_instance.db


async def create_indexes():
    db = db_instance.db
    # users
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    # tokens
    await db.tokens.create_index("refresh_token", unique=True)
    await db.tokens.create_index("user_id")
    await db.tokens.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    # audit_logs
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("event_type")
    await db.audit_logs.create_index("timestamp")
    # service_logs
    await db.service_logs.create_index("request_id", unique=True)
    await db.service_logs.create_index("timestamp")
    print("MongoDB indexes created.")
