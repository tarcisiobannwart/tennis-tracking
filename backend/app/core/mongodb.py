"""
MongoDB database connection and configuration
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database = None


db = MongoDB()


async def connect_mongodb():
    """Create database connection"""
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL.split('@')[-1]}")

        # Create client
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=50,
            minPoolSize=10
        )

        # Get database
        db.database = db.client[settings.DATABASE_NAME]

        # Verify connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")

        # Create indexes if needed
        await create_indexes()

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def disconnect_mongodb():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create database indexes"""
    try:
        # Users collection indexes
        users = db.database.users
        await users.create_index("email", unique=True)
        await users.create_index("username", unique=True)
        await users.create_index("createdAt")
        await users.create_index("role")
        await users.create_index("subscription.plan")
        await users.create_index("organizationId")
        await users.create_index("emailVerificationToken", sparse=True)
        await users.create_index("passwordResetToken", sparse=True)

        # Matches collection indexes
        matches = db.database.matches
        await matches.create_index("date")
        await matches.create_index([("player1.id", 1), ("player2.id", 1)])
        await matches.create_index("status")
        await matches.create_index("tournament")

        # Videos collection indexes
        videos = db.database.videos
        await videos.create_index("userId")
        await videos.create_index("uploadedAt")
        await videos.create_index("status")

        # Analysis tasks collection indexes
        tasks = db.database.analysis_tasks
        await tasks.create_index("taskId", unique=True)
        await tasks.create_index("userId")
        await tasks.create_index("status")
        await tasks.create_index("createdAt")

        # Player stats collection indexes
        stats = db.database.player_stats
        await stats.create_index([("playerId", 1), ("matchId", 1)])
        await stats.create_index("playerId")

        # Game events collection indexes
        events = db.database.game_events
        await events.create_index([("matchId", 1), ("timestamp", 1)])
        await events.create_index("eventType")

        # Streams collection indexes
        streams_col = db.database.streams
        await streams_col.create_index("streamKey", unique=True)
        await streams_col.create_index("userId")
        await streams_col.create_index("matchId")
        await streams_col.create_index("status")
        await streams_col.create_index("createdAt")

        # Organizations collection indexes
        orgs = db.database.organizations
        await orgs.create_index("slug", unique=True)
        await orgs.create_index("ownerId")
        await orgs.create_index("members.userId")

        # Organization invites collection indexes
        invites = db.database.organization_invites
        await invites.create_index("token", unique=True)
        await invites.create_index("organizationId")
        await invites.create_index([("organizationId", 1), ("email", 1)])
        await invites.create_index("expiresAt", expireAfterSeconds=0)

        # Activity logs collection indexes
        logs = db.database.activity_logs
        await logs.create_index("userId")
        await logs.create_index("action")
        await logs.create_index("createdAt")
        await logs.create_index([("userId", 1), ("action", 1), ("createdAt", -1)])

        # Subscription events collection indexes
        sub_events = db.database.subscription_events
        await sub_events.create_index("stripeEventId", unique=True)
        await sub_events.create_index("userId")

        logger.info("Database indexes created successfully")

    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


async def close_mongodb():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


def get_database():
    """Get database instance"""
    return db.database


def get_collection(name: str):
    """Get database collection by name"""
    if db.database is None:
        raise RuntimeError("Database not connected")
    return db.database[name]
