"""
Seed script — inserts sample users into the truadnaDev database.
Run once:  python seed_data.py
"""
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

MONGO_URI = "mongodb+srv://HalMan_db_user:Halcyon%4012$@cluster0.ifvwnf.mongodb.net/"
DB_NAME = "truadnaDev"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SAMPLE_USERS = [
    {
        "username": "admin",
        "email": "admin@truedna.com",
        "password": "Admin@1234",
    },
    {
        "username": "john_doe",
        "email": "john.doe@truedna.com",
        "password": "John@5678",
    },
    {
        "username": "jane_smith",
        "email": "jane.smith@truedna.com",
        "password": "Jane@9012",
    },
    {
        "username": "test_user",
        "email": "test@truedna.com",
        "password": "Test@3456",
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    users_col = db["users"]

    inserted = 0
    skipped = 0

    for u in SAMPLE_USERS:
        existing = await users_col.find_one({"username": u["username"]})
        if existing:
            print(f"  [SKIP]   {u['username']} already exists")
            skipped += 1
            continue

        doc = {
            "username": u["username"],
            "email": u["email"],
            "hashed_password": pwd_context.hash(u["password"]),
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "last_login": None,
        }
        result = await users_col.insert_one(doc)
        print(f"  [INSERT] {u['username']} -> {result.inserted_id}  (password: {u['password']})")
        inserted += 1

    client.close()
    print(f"\nDone. {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    asyncio.run(seed())
