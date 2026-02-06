"""
User service - CRUD, password management, profile
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId

from app.core.mongodb import get_collection
from app.core.auth import get_password_hash, verify_password
from app.models.user import UserCreate, UserUpdate, UserSubscription, SubscriptionPlan


class UserService:
    """Service for user management"""

    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_collection("users")
        return self._collection

    async def get_by_id(self, user_id: str) -> Optional[dict]:
        return await self.collection.find_one({"_id": user_id})

    async def get_by_email(self, email: str) -> Optional[dict]:
        return await self.collection.find_one({"email": email})

    async def get_by_username(self, username: str) -> Optional[dict]:
        return await self.collection.find_one({"username": username})

    async def create(self, user_data: UserCreate) -> dict:
        user_dict = user_data.dict()
        user_dict["password"] = get_password_hash(user_data.password)
        user_dict["createdAt"] = datetime.utcnow()
        user_dict["updatedAt"] = datetime.utcnow()
        user_dict["emailVerified"] = False
        user_dict["subscription"] = UserSubscription().dict()

        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        return user_dict

    async def update(self, user_id: str, update_data: dict) -> Optional[dict]:
        update_data["updatedAt"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        return await self.get_by_id(user_id)

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        if not verify_password(current_password, user["password"]):
            return False
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {
                "password": get_password_hash(new_password),
                "updatedAt": datetime.utcnow()
            }}
        )
        return True

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        user = await self.get_by_email(email)
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "passwordResetToken": token,
                "passwordResetExpires": datetime.utcnow() + timedelta(hours=1)
            }}
        )
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        user = await self.collection.find_one({
            "passwordResetToken": token,
            "passwordResetExpires": {"$gt": datetime.utcnow()}
        })
        if not user:
            return False
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "password": get_password_hash(new_password),
                "passwordResetToken": None,
                "passwordResetExpires": None,
                "updatedAt": datetime.utcnow()
            }}
        )
        return True

    async def create_email_verification_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"emailVerificationToken": token}}
        )
        return token

    async def verify_email(self, token: str) -> bool:
        user = await self.collection.find_one({"emailVerificationToken": token})
        if not user:
            return False
        await self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "emailVerified": True,
                "emailVerificationToken": None,
                "updatedAt": datetime.utcnow()
            }}
        )
        return True

    async def update_subscription(self, user_id: str, subscription: dict) -> Optional[dict]:
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {
                "subscription": subscription,
                "updatedAt": datetime.utcnow()
            }}
        )
        return await self.get_by_id(user_id)

    async def get_video_count_this_month(self, user_id: str) -> int:
        videos = get_collection("videos")
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        count = await videos.count_documents({
            "userId": user_id,
            "uploadedAt": {"$gte": first_of_month}
        })
        return count

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        plan: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[list, int]:
        query = {}
        if role:
            query["role"] = role
        if plan:
            query["subscription.plan"] = plan
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"fullName": {"$regex": search, "$options": "i"}},
            ]

        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)

        for user in users:
            user["_id"] = str(user["_id"])
            user.pop("password", None)
            user.pop("refreshToken", None)

        return users, total


user_service = UserService()
