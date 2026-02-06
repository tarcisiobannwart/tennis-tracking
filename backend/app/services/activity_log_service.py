"""
Activity log service
"""
from datetime import datetime
from typing import Optional
from app.core.mongodb import get_collection


class ActivityLogService:
    """Service for logging user activity"""

    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = get_collection("activity_logs")
        return self._collection

    async def log(
        self,
        user_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        await self.collection.insert_one({
            "userId": user_id,
            "action": action,
            "resource": resource,
            "resourceId": resource_id,
            "details": details or {},
            "ipAddress": ip_address,
            "userAgent": user_agent,
            "createdAt": datetime.utcnow(),
        })

    async def get_user_logs(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
    ) -> tuple[list, int]:
        query = {"userId": user_id}
        if action:
            query["action"] = action

        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)

        for log in logs:
            log["_id"] = str(log["_id"])

        return logs, total

    async def get_all_logs(
        self,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> tuple[list, int]:
        query = {}
        if action:
            query["action"] = action
        if user_id:
            query["userId"] = user_id

        total = await self.collection.count_documents(query)
        cursor = self.collection.find(query).sort("createdAt", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)

        for log in logs:
            log["_id"] = str(log["_id"])

        return logs, total


activity_log_service = ActivityLogService()
