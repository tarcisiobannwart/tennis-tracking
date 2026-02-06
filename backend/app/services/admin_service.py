"""
Admin service - metrics, user management
"""
from datetime import datetime, timedelta
from typing import Optional
from app.core.mongodb import get_collection


class AdminService:
    """Service for admin operations"""

    async def get_dashboard_metrics(self) -> dict:
        users = get_collection("users")
        videos = get_collection("videos")

        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        total_users = await users.count_documents({})
        new_users_month = await users.count_documents({"createdAt": {"$gte": first_of_month}})
        active_users = await users.count_documents({"isActive": True})
        total_videos = await videos.count_documents({})

        # Subscription breakdown
        rally_count = await users.count_documents({"subscription.plan": "rally"})
        match_point_count = await users.count_documents({"subscription.plan": "match_point"})
        grand_slam_count = await users.count_documents({"subscription.plan": "grand_slam"})

        # MRR calculation
        mrr = (match_point_count * 9700 + grand_slam_count * 29700) / 100  # em reais

        # Role breakdown
        admin_count = await users.count_documents({"role": "admin"})
        coach_count = await users.count_documents({"role": "coach"})
        player_count = await users.count_documents({"role": "player"})

        return {
            "totalUsers": total_users,
            "newUsersThisMonth": new_users_month,
            "activeUsers": active_users,
            "totalVideos": total_videos,
            "mrr": mrr,
            "subscriptions": {
                "rally": rally_count,
                "match_point": match_point_count,
                "grand_slam": grand_slam_count,
            },
            "roles": {
                "admin": admin_count,
                "coach": coach_count,
                "player": player_count,
            },
        }

    async def update_user_role(self, user_id: str, role: str) -> bool:
        users = get_collection("users")
        result = await users.update_one(
            {"_id": user_id},
            {"$set": {"role": role, "updatedAt": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def update_user_plan(self, user_id: str, plan: str) -> bool:
        users = get_collection("users")
        result = await users.update_one(
            {"_id": user_id},
            {"$set": {
                "subscription.plan": plan,
                "subscription.status": "active",
                "updatedAt": datetime.utcnow(),
            }}
        )
        return result.modified_count > 0

    async def toggle_user_active(self, user_id: str, is_active: bool) -> bool:
        users = get_collection("users")
        result = await users.update_one(
            {"_id": user_id},
            {"$set": {"isActive": is_active, "updatedAt": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def get_subscription_stats(self) -> dict:
        users = get_collection("users")
        sub_events = get_collection("subscription_events")

        pipeline = [
            {"$group": {
                "_id": "$subscription.plan",
                "count": {"$sum": 1},
            }}
        ]
        plan_counts = {}
        async for doc in users.aggregate(pipeline):
            plan_counts[doc["_id"]] = doc["count"]

        recent_events = await sub_events.find({}).sort("createdAt", -1).limit(20).to_list(20)
        for event in recent_events:
            event["_id"] = str(event["_id"])

        return {
            "planBreakdown": plan_counts,
            "recentEvents": recent_events,
        }


admin_service = AdminService()
