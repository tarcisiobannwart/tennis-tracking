"""
Seed script - creates admin user and initial data
Run with: python -m scripts.seed_data
"""
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MONGODB_URL = "mongodb://admin:tennis_admin_2024@localhost:27017/tennis_tracking?authSource=admin"
DATABASE_NAME = "tennis_tracking"


async def seed():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    # Create admin user
    admin_username = "29449799814"
    admin_email = "admin@tennistrack.app"
    admin_password = "Theo78745382!"

    existing = await db.users.find_one({"username": admin_username})
    if existing:
        print(f"Admin user '{admin_username}' already exists, updating...")
        await db.users.update_one(
            {"username": admin_username},
            {"$set": {
                "role": "admin",
                "subscription": {
                    "plan": "grand_slam",
                    "status": "active",
                    "stripeCustomerId": None,
                    "stripeSubscriptionId": None,
                    "currentPeriodStart": None,
                    "currentPeriodEnd": None,
                    "cancelAtPeriodEnd": False,
                    "trialEnd": None,
                },
                "emailVerified": True,
                "isActive": True,
                "updatedAt": datetime.utcnow(),
            }}
        )
    else:
        admin_doc = {
            "email": admin_email,
            "username": admin_username,
            "fullName": "Administrador",
            "role": "admin",
            "isActive": True,
            "password": pwd_context.hash(admin_password),
            "language": "pt-BR",
            "preferences": {},
            "emailVerified": True,
            "subscription": {
                "plan": "grand_slam",
                "status": "active",
                "stripeCustomerId": None,
                "stripeSubscriptionId": None,
                "currentPeriodStart": None,
                "currentPeriodEnd": None,
                "cancelAtPeriodEnd": False,
                "trialEnd": None,
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        result = await db.users.insert_one(admin_doc)
        print(f"Admin user created with id: {result.inserted_id}")

    print("Seed complete!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
