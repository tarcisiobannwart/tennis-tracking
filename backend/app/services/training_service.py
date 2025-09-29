"""
Training service for training session and drill management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.models.training import TrainingSession, DrillType, TrainingDrill, SessionStatus
from app.schemas.training import (
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingDrillCreate
)

logger = structlog.get_logger(__name__)


class TrainingService:
    """Service for training-related operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_drill_types(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[DrillType]:
        """Get available drill types"""

        query = select(DrillType)

        # Apply filters
        if category:
            query = query.where(DrillType.category == category)

        if difficulty:
            query = query.where(DrillType.difficulty == difficulty)

        query = query.order_by(DrillType.name).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_training_session(self, session_data: TrainingSessionCreate) -> TrainingSession:
        """Create a new training session"""

        session = TrainingSession(
            player_id=session_data.player_id,
            title=session_data.title,
            description=session_data.description,
            session_type=session_data.session_type,
            scheduled_at=session_data.scheduled_at,
            objectives=session_data.objectives,
            focus_areas=session_data.focus_areas,
            coach_name=session_data.coach_name
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        logger.info("Training session created", session_id=session.id, title=session.title)
        return session

    async def get_training_sessions(
        self,
        skip: int = 0,
        limit: int = 50,
        player_id: Optional[str] = None,
        status: Optional[str] = None,
        session_type: Optional[str] = None
    ) -> List[TrainingSession]:
        """Get training sessions with optional filtering"""

        query = select(TrainingSession)

        # Apply filters
        if player_id:
            query = query.where(TrainingSession.player_id == player_id)

        if status:
            query = query.where(TrainingSession.status == status)

        if session_type:
            query = query.where(TrainingSession.session_type == session_type)

        query = query.order_by(desc(TrainingSession.scheduled_at)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_training_session(self, session_id: str) -> Optional[TrainingSession]:
        """Get a single training session by ID"""

        query = select(TrainingSession).where(TrainingSession.id == session_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_training_session(
        self,
        session_id: str,
        session_data: TrainingSessionUpdate
    ) -> Optional[TrainingSession]:
        """Update a training session"""

        session = await self.get_training_session(session_id)
        if not session:
            return None

        # Update fields that are provided
        update_data = session_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(session, field, value)

        session.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(session)

        logger.info("Training session updated", session_id=session_id)
        return session

    async def delete_training_session(self, session_id: str) -> bool:
        """Delete a training session"""

        session = await self.get_training_session(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()

        logger.info("Training session deleted", session_id=session_id)
        return True

    async def add_drill_to_session(
        self,
        session_id: str,
        drill_data: TrainingDrillCreate
    ) -> Optional[TrainingDrill]:
        """Add a drill to a training session"""

        session = await self.get_training_session(session_id)
        if not session:
            return None

        drill = TrainingDrill(
            training_session_id=session_id,
            drill_type_id=drill_data.drill_type_id,
            order_in_session=drill_data.order_in_session,
            duration_minutes=drill_data.duration_minutes,
            repetitions=drill_data.repetitions,
            sets=drill_data.sets
        )

        self.db.add(drill)
        await self.db.commit()
        await self.db.refresh(drill)

        logger.info("Drill added to session", drill_id=drill.id, session_id=session_id)
        return drill

    async def update_training_drill(
        self,
        drill_id: str,
        drill_updates: Dict[str, Any]
    ) -> Optional[TrainingDrill]:
        """Update a training drill"""

        query = select(TrainingDrill).where(TrainingDrill.id == drill_id)
        result = await self.db.execute(query)
        drill = result.scalar_one_or_none()

        if not drill:
            return None

        # Update fields
        for field, value in drill_updates.items():
            if hasattr(drill, field):
                setattr(drill, field, value)

        drill.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(drill)

        logger.info("Training drill updated", drill_id=drill_id)
        return drill

    async def start_training_session(self, session_id: str) -> Optional[TrainingSession]:
        """Start a training session"""

        session = await self.get_training_session(session_id)
        if not session:
            return None

        if session.status != SessionStatus.PLANNED:
            raise ValueError(f"Session must be planned to start. Current status: {session.status}")

        session.status = SessionStatus.IN_PROGRESS
        session.started_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(session)

        logger.info("Training session started", session_id=session_id)
        return session

    async def finish_training_session(self, session_id: str) -> Optional[TrainingSession]:
        """Finish a training session"""

        session = await self.get_training_session(session_id)
        if not session:
            return None

        if session.status != SessionStatus.IN_PROGRESS:
            raise ValueError(f"Session must be in progress to finish. Current status: {session.status}")

        session.status = SessionStatus.COMPLETED
        session.finished_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        # Calculate duration
        if session.started_at and session.finished_at:
            duration = session.finished_at - session.started_at
            session.duration_minutes = int(duration.total_seconds() / 60)

        await self.db.commit()
        await self.db.refresh(session)

        logger.info("Training session finished", session_id=session_id)
        return session

    async def get_training_progress(
        self,
        player_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Get training progress for a player"""

        # Get cutoff date based on period
        cutoff_date = self._get_period_cutoff(period)

        # Get training sessions in period
        sessions_query = select(TrainingSession).where(
            and_(
                TrainingSession.player_id == player_id,
                TrainingSession.scheduled_at >= cutoff_date
            )
        )

        sessions_result = await self.db.execute(sessions_query)
        sessions = sessions_result.scalars().all()

        # Calculate progress metrics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == SessionStatus.COMPLETED])
        total_duration = sum([s.duration_minutes for s in sessions if s.duration_minutes])

        # Group by session type
        session_types = {}
        for session in sessions:
            if session.session_type not in session_types:
                session_types[session.session_type] = 0
            session_types[session.session_type] += 1

        # Calculate average ratings
        ratings = [s.effort_rating for s in sessions if s.effort_rating]
        average_effort = sum(ratings) / len(ratings) if ratings else 0

        intensity_ratings = [s.intensity_level for s in sessions if s.intensity_level]
        average_intensity = sum(intensity_ratings) / len(intensity_ratings) if intensity_ratings else 0

        return {
            "player_id": player_id,
            "period": period,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "total_duration_minutes": total_duration,
            "average_session_duration": total_duration / completed_sessions if completed_sessions > 0 else 0,
            "session_types_breakdown": session_types,
            "average_effort_rating": average_effort,
            "average_intensity_level": average_intensity,
            "recent_sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "date": s.scheduled_at,
                    "status": s.status,
                    "duration": s.duration_minutes
                }
                for s in sessions[-5:]  # Last 5 sessions
            ]
        }

    async def get_training_analytics(
        self,
        player_id: str,
        session_type: Optional[str] = None,
        period: str = "month"
    ) -> Dict[str, Any]:
        """Get training analytics for a player"""

        cutoff_date = self._get_period_cutoff(period)

        # Base query
        query = select(TrainingSession).where(
            and_(
                TrainingSession.player_id == player_id,
                TrainingSession.scheduled_at >= cutoff_date
            )
        )

        if session_type:
            query = query.where(TrainingSession.session_type == session_type)

        result = await self.db.execute(query)
        sessions = result.scalars().all()

        # Analytics calculations
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s.status == SessionStatus.COMPLETED]

        # Performance trends
        weekly_sessions = {}
        for session in sessions:
            week_key = session.scheduled_at.strftime("%Y-W%U")
            if week_key not in weekly_sessions:
                weekly_sessions[week_key] = 0
            weekly_sessions[week_key] += 1

        # Focus areas analysis
        focus_areas = {}
        for session in sessions:
            if session.focus_areas:
                for area in session.focus_areas:
                    if area not in focus_areas:
                        focus_areas[area] = 0
                    focus_areas[area] += 1

        return {
            "player_id": player_id,
            "period": period,
            "session_type": session_type,
            "total_sessions": total_sessions,
            "completed_sessions": len(completed_sessions),
            "weekly_distribution": weekly_sessions,
            "focus_areas_frequency": focus_areas,
            "performance_metrics": {
                "consistency": self._calculate_consistency(sessions),
                "improvement_trend": self._calculate_improvement_trend(sessions),
                "intensity_progression": self._calculate_intensity_progression(sessions)
            },
            "recommendations": self._generate_training_recommendations(sessions)
        }

    async def get_training_recommendations(
        self,
        player_id: str,
        focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-powered training recommendations"""

        # Get recent training history
        recent_sessions_query = select(TrainingSession).where(
            and_(
                TrainingSession.player_id == player_id,
                TrainingSession.scheduled_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).order_by(desc(TrainingSession.scheduled_at)).limit(10)

        recent_result = await self.db.execute(recent_sessions_query)
        recent_sessions = recent_result.scalars().all()

        # Generate recommendations based on training history
        recommendations = {
            "primary_recommendations": [
                "Increase serve practice frequency",
                "Focus on endurance training",
                "Work on footwork drills"
            ],
            "focus_area_suggestions": {
                "technique": ["Forehand accuracy drills", "Backhand consistency"],
                "fitness": ["Cardio intervals", "Strength training"],
                "tactical": ["Match simulation", "Pattern play"]
            },
            "weekly_schedule": {
                "monday": "Technique focus - serve and volley",
                "tuesday": "Fitness - cardio and agility",
                "wednesday": "Match play simulation",
                "thursday": "Recovery and flexibility",
                "friday": "Tactical drills",
                "saturday": "Match or competitive play",
                "sunday": "Rest or light practice"
            },
            "improvement_areas": self._identify_improvement_areas(recent_sessions),
            "next_session_suggestion": self._suggest_next_session(recent_sessions, focus_area)
        }

        return recommendations

    async def get_training_calendar(
        self,
        player_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get training calendar for a player"""

        # Parse dates
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        else:
            start_dt = datetime.utcnow() - timedelta(days=30)

        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = datetime.utcnow() + timedelta(days=30)

        # Get sessions in date range
        sessions_query = select(TrainingSession).where(
            and_(
                TrainingSession.player_id == player_id,
                TrainingSession.scheduled_at >= start_dt,
                TrainingSession.scheduled_at <= end_dt
            )
        ).order_by(TrainingSession.scheduled_at)

        result = await self.db.execute(sessions_query)
        sessions = result.scalars().all()

        # Format calendar data
        calendar_events = []
        for session in sessions:
            calendar_events.append({
                "id": session.id,
                "title": session.title,
                "start": session.scheduled_at.isoformat(),
                "end": (session.finished_at or session.scheduled_at + timedelta(hours=2)).isoformat(),
                "type": session.session_type,
                "status": session.status,
                "coach": session.coach_name,
                "description": session.description
            })

        return {
            "player_id": player_id,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "events": calendar_events,
            "summary": {
                "total_sessions": len(sessions),
                "completed": len([s for s in sessions if s.status == SessionStatus.COMPLETED]),
                "planned": len([s for s in sessions if s.status == SessionStatus.PLANNED]),
                "in_progress": len([s for s in sessions if s.status == SessionStatus.IN_PROGRESS])
            }
        }

    def _get_period_cutoff(self, period: str) -> datetime:
        """Get cutoff date for period filtering"""

        now = datetime.utcnow()

        if period == "year":
            return now - timedelta(days=365)
        elif period == "quarter":
            return now - timedelta(days=90)
        elif period == "month":
            return now - timedelta(days=30)
        elif period == "week":
            return now - timedelta(days=7)
        else:
            return datetime.min

    def _calculate_consistency(self, sessions: List[TrainingSession]) -> float:
        """Calculate training consistency score"""
        if not sessions:
            return 0.0

        # Simple consistency metric based on session frequency
        completed = [s for s in sessions if s.status == SessionStatus.COMPLETED]
        return (len(completed) / len(sessions)) * 100

    def _calculate_improvement_trend(self, sessions: List[TrainingSession]) -> str:
        """Calculate improvement trend"""
        if len(sessions) < 3:
            return "insufficient_data"

        # Analyze effort ratings over time
        recent_ratings = [s.effort_rating for s in sessions[-5:] if s.effort_rating]
        earlier_ratings = [s.effort_rating for s in sessions[:-5] if s.effort_rating]

        if not recent_ratings or not earlier_ratings:
            return "insufficient_data"

        recent_avg = sum(recent_ratings) / len(recent_ratings)
        earlier_avg = sum(earlier_ratings) / len(earlier_ratings)

        if recent_avg > earlier_avg + 0.5:
            return "improving"
        elif recent_avg < earlier_avg - 0.5:
            return "declining"
        else:
            return "stable"

    def _calculate_intensity_progression(self, sessions: List[TrainingSession]) -> Dict[str, Any]:
        """Calculate intensity progression"""
        intensity_data = []

        for session in sessions:
            if session.intensity_level:
                intensity_data.append({
                    "date": session.scheduled_at.isoformat(),
                    "intensity": session.intensity_level
                })

        return {
            "data_points": intensity_data,
            "average_intensity": sum([d["intensity"] for d in intensity_data]) / len(intensity_data) if intensity_data else 0,
            "trend": "increasing" if len(intensity_data) > 1 and intensity_data[-1]["intensity"] > intensity_data[0]["intensity"] else "stable"
        }

    def _generate_training_recommendations(self, sessions: List[TrainingSession]) -> List[str]:
        """Generate training recommendations based on history"""
        recommendations = []

        if not sessions:
            recommendations.append("Start with basic fitness assessment")
            return recommendations

        # Analyze session types
        session_types = [s.session_type for s in sessions]
        technique_sessions = session_types.count("technique")
        fitness_sessions = session_types.count("fitness")

        if technique_sessions < fitness_sessions:
            recommendations.append("Increase technical training sessions")

        if len([s for s in sessions if s.intensity_level and s.intensity_level > 7]) < len(sessions) * 0.3:
            recommendations.append("Include more high-intensity training")

        return recommendations

    def _identify_improvement_areas(self, sessions: List[TrainingSession]) -> List[str]:
        """Identify areas for improvement based on session data"""
        areas = []

        # Analyze focus areas frequency
        focus_areas = {}
        for session in sessions:
            if session.focus_areas:
                for area in session.focus_areas:
                    focus_areas[area] = focus_areas.get(area, 0) + 1

        # Find least practiced areas
        if focus_areas:
            min_count = min(focus_areas.values())
            least_practiced = [area for area, count in focus_areas.items() if count == min_count]
            areas.extend(least_practiced)

        return areas

    def _suggest_next_session(self, sessions: List[TrainingSession], focus_area: Optional[str] = None) -> Dict[str, Any]:
        """Suggest next training session"""
        if not sessions:
            return {
                "type": "fitness",
                "duration": 60,
                "focus": "basic fitness assessment",
                "intensity": 5
            }

        last_session = sessions[0]  # Most recent

        # Suggest complementary session type
        if last_session.session_type == "fitness":
            suggested_type = "technique"
        elif last_session.session_type == "technique":
            suggested_type = "tactical"
        else:
            suggested_type = "fitness"

        return {
            "type": suggested_type,
            "duration": 90,
            "focus": focus_area or f"{suggested_type} development",
            "intensity": 6,
            "objectives": [f"Improve {suggested_type} skills", "Build consistency"],
            "suggested_drills": self._get_suggested_drills(suggested_type)
        }

    def _get_suggested_drills(self, session_type: str) -> List[str]:
        """Get suggested drills for session type"""
        drill_suggestions = {
            "technique": ["Serve practice", "Forehand cross-court", "Backhand down-the-line"],
            "fitness": ["Sprint intervals", "Agility ladder", "Core strengthening"],
            "tactical": ["Point construction", "Pattern recognition", "Match simulation"]
        }

        return drill_suggestions.get(session_type, ["General practice"])