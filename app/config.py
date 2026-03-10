import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "hrms_lite")


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    db_instance.db = db_instance.client[DATABASE_NAME]

    # Create indexes
    await db_instance.db.employees.create_index("employee_id", unique=True)
    await db_instance.db.employees.create_index("email", unique=True)
    await db_instance.db.attendance.create_index(
        [("employee_id", 1), ("date", 1)], unique=True
    )
    print(f"Connected to MongoDB: {DATABASE_NAME}")


async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed")


def get_database():
    return db_instance.db
