"""
Training service for MongoDB-based training session and drill management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import structlog

from app.core.mongodb import get_collection
from app.models.training import (
    SessionStatus,
    TrainingSessionCreate,
    TrainingSessionUpdate,
    TrainingDrillCreate,
    DrillTypeCreate,
)
from app.services.analytics_service import AnalyticsService

logger = structlog.get_logger(__name__)

DRILL_SEED_DATA = [
    {"name": "Forehand Cross-Court", "description": "Praticar forehand cruzado com consistencia", "category": "technique", "difficulty": "beginner", "duration_minutes": 15, "equipment_needed": ["raquete", "bolas"], "instructions": "Posicione-se na baseline e execute forehand cruzado repetidamente."},
    {"name": "Backhand Down-the-Line", "description": "Backhand paralelo com precisao", "category": "technique", "difficulty": "intermediate", "duration_minutes": 15, "equipment_needed": ["raquete", "bolas"], "instructions": "Execute backhand paralelo mantendo a bola dentro da linha."},
    {"name": "Serve Flat", "description": "Saque rapido e reto", "category": "serve", "difficulty": "intermediate", "duration_minutes": 20, "equipment_needed": ["raquete", "bolas"], "instructions": "Pratique o saque flat mirando no T e no canto."},
    {"name": "Serve Slice", "description": "Saque com efeito lateral", "category": "serve", "difficulty": "advanced", "duration_minutes": 20, "equipment_needed": ["raquete", "bolas"], "instructions": "Execute saque slice abrindo o angulo para fora da quadra."},
    {"name": "Volley Net Approach", "description": "Subida a rede com voleio", "category": "volley", "difficulty": "intermediate", "duration_minutes": 15, "equipment_needed": ["raquete", "bolas"], "instructions": "Aproxime-se da rede e execute voleios curtos."},
    {"name": "Sprint Intervals", "description": "Sprints de alta intensidade na quadra", "category": "fitness", "difficulty": "advanced", "duration_minutes": 10, "equipment_needed": ["cones"], "instructions": "Sprint de baseline a rede, 10 repeticoes com 30s descanso."},
    {"name": "Ladder Drills", "description": "Exercicios de coordenacao e agilidade", "category": "footwork", "difficulty": "beginner", "duration_minutes": 10, "equipment_needed": ["escada de agilidade"], "instructions": "Execute padroes variados na escada de agilidade."},
    {"name": "Pattern Play", "description": "Construcao tatica de pontos", "category": "tactical", "difficulty": "advanced", "duration_minutes": 25, "equipment_needed": ["raquete", "bolas", "cones"], "instructions": "Pratique sequencias taticas: saque, forehand aberto, approach, voleio."},
    {"name": "Return of Serve", "description": "Devolucao de saque com posicionamento", "category": "return", "difficulty": "intermediate", "duration_minutes": 15, "equipment_needed": ["raquete", "bolas"], "instructions": "Pratique devolver saques variados com controle de profundidade."},
    {"name": "Mental Focus Drill", "description": "Exercicio de concentracao e visualizacao", "category": "mental", "difficulty": "beginner", "duration_minutes": 10, "equipment_needed": [], "instructions": "5 min de respiracao + 5 min de visualizacao de pontos jogados."},
    {"name": "Drop Shot Practice", "description": "Deixadinha com toque fino", "category": "technique", "difficulty": "advanced", "duration_minutes": 15, "equipment_needed": ["raquete", "bolas"], "instructions": "Pratique drop shots de diferentes posicoes da quadra."},
    {"name": "Core Strengthening", "description": "Fortalecimento do core para estabilidade", "category": "fitness", "difficulty": "beginner", "duration_minutes": 20, "equipment_needed": ["tapete"], "instructions": "Prancha, russian twist, bicycle crunches - 3 series de 15."},
]


class TrainingService:
    """Service for training operations with MongoDB"""

    def __init__(self):
        self.analytics_service = AnalyticsService()

    async def seed_drill_types(self) -> int:
        """Seed default drill types if collection is empty"""
        drills = get_collection("drill_types")
        count = await drills.count_documents({})
        if count > 0:
            return count

        now = datetime.utcnow()
        docs = []
        for d in DRILL_SEED_DATA:
            docs.append({
                "_id": str(uuid.uuid4()),
                **d,
                "created_at": now,
                "updated_at": None,
            })
        await drills.insert_many(docs)
        logger.info("Seeded drill types", count=len(docs))
        return len(docs)

    async def get_drill_types(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[dict]:
        drills = get_collection("drill_types")
        query: dict = {}
        if category:
            query["category"] = category
        if difficulty:
            query["difficulty"] = difficulty

        cursor = drills.find(query).sort("name", 1).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            results.append(doc)
        return results

    async def create_drill_type(self, data: DrillTypeCreate) -> dict:
        drills = get_collection("drill_types")
        now = datetime.utcnow()
        doc = {
            "_id": str(uuid.uuid4()),
            **data.model_dump(),
            "created_at": now,
            "updated_at": None,
        }
        await drills.insert_one(doc)
        doc["id"] = doc.pop("_id")
        return doc

    # --- Training Sessions ---

    async def create_session(self, user_id: str, data: TrainingSessionCreate) -> dict:
        sessions = get_collection("training_sessions")
        now = datetime.utcnow()
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            **data.model_dump(),
            "scheduled_at": data.scheduled_at,
            "status": SessionStatus.PLANNED.value,
            "started_at": None,
            "finished_at": None,
            "duration_minutes": None,
            "coach_notes": None,
            "intensity_level": None,
            "effort_rating": None,
            "fatigue_level": None,
            "session_notes": None,
            "player_feedback": None,
            "drills": [],
            "created_at": now,
            "updated_at": None,
        }
        await sessions.insert_one(doc)
        logger.info("Training session created", session_id=doc["_id"])
        doc["id"] = doc.pop("_id")
        return doc

    async def get_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        session_type: Optional[str] = None,
    ) -> List[dict]:
        sessions = get_collection("training_sessions")
        query: dict = {"user_id": user_id}
        if status:
            query["status"] = status
        if session_type:
            query["session_type"] = session_type

        cursor = sessions.find(query).sort("scheduled_at", -1).skip(skip).limit(limit)
        results = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            results.append(doc)
        return results

    async def get_session(self, session_id: str, user_id: str) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        doc = await sessions.find_one({"_id": session_id, "user_id": user_id})
        if doc:
            doc["id"] = doc.pop("_id")
        return doc

    async def update_session(self, session_id: str, user_id: str, data: TrainingSessionUpdate) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        update_data = {k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None}
        if not update_data:
            return await self.get_session(session_id, user_id)

        update_data["updated_at"] = datetime.utcnow()
        result = await sessions.update_one(
            {"_id": session_id, "user_id": user_id},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return None
        return await self.get_session(session_id, user_id)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        sessions = get_collection("training_sessions")
        result = await sessions.delete_one({"_id": session_id, "user_id": user_id})
        return result.deleted_count > 0

    async def start_session(self, session_id: str, user_id: str) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        doc = await sessions.find_one({"_id": session_id, "user_id": user_id})
        if not doc:
            return None
        if doc["status"] != SessionStatus.PLANNED.value:
            return None

        now = datetime.utcnow()
        await sessions.update_one(
            {"_id": session_id},
            {"$set": {
                "status": SessionStatus.IN_PROGRESS.value,
                "started_at": now,
                "updated_at": now,
            }}
        )
        return await self.get_session(session_id, user_id)

    async def finish_session(self, session_id: str, user_id: str) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        doc = await sessions.find_one({"_id": session_id, "user_id": user_id})
        if not doc:
            return None
        if doc["status"] != SessionStatus.IN_PROGRESS.value:
            return None

        now = datetime.utcnow()
        duration = None
        if doc.get("started_at"):
            duration = int((now - doc["started_at"]).total_seconds() / 60)

        await sessions.update_one(
            {"_id": session_id},
            {"$set": {
                "status": SessionStatus.COMPLETED.value,
                "finished_at": now,
                "duration_minutes": duration,
                "updated_at": now,
            }}
        )
        return await self.get_session(session_id, user_id)

    # --- Drills within Session ---

    async def add_drill_to_session(self, session_id: str, user_id: str, data: TrainingDrillCreate) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        doc = await sessions.find_one({"_id": session_id, "user_id": user_id})
        if not doc:
            return None

        drill_doc = {
            "id": str(uuid.uuid4()),
            **data.model_dump(),
            "success_rate": None,
            "accuracy_score": None,
            "drill_data": None,
            "started_at": None,
            "finished_at": None,
            "notes": None,
            "coach_feedback": None,
        }
        await sessions.update_one(
            {"_id": session_id},
            {"$push": {"drills": drill_doc}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return await self.get_session(session_id, user_id)

    async def update_drill_in_session(
        self, session_id: str, user_id: str, drill_id: str, updates: dict
    ) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        set_fields = {}
        for key, val in updates.items():
            set_fields[f"drills.$.{key}"] = val
        set_fields["updated_at"] = datetime.utcnow()

        await sessions.update_one(
            {"_id": session_id, "user_id": user_id, "drills.id": drill_id},
            {"$set": set_fields}
        )
        return await self.get_session(session_id, user_id)

    async def remove_drill_from_session(self, session_id: str, user_id: str, drill_id: str) -> Optional[dict]:
        sessions = get_collection("training_sessions")
        await sessions.update_one(
            {"_id": session_id, "user_id": user_id},
            {"$pull": {"drills": {"id": drill_id}}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return await self.get_session(session_id, user_id)

    # --- Progress & Analytics ---

    async def get_progress(self, user_id: str, period: str = "month") -> dict:
        sessions = get_collection("training_sessions")
        cutoff = self._get_period_cutoff(period)

        query = {"user_id": user_id, "scheduled_at": {"$gte": cutoff}}
        docs = []
        async for doc in sessions.find(query).sort("scheduled_at", -1):
            docs.append(doc)

        total = len(docs)
        completed = [d for d in docs if d["status"] == SessionStatus.COMPLETED.value]
        total_duration = sum(d.get("duration_minutes", 0) or 0 for d in completed)

        session_types: Dict[str, int] = {}
        for d in docs:
            st = d.get("session_type", "other")
            session_types[st] = session_types.get(st, 0) + 1

        ratings = [d["effort_rating"] for d in docs if d.get("effort_rating")]
        avg_effort = sum(ratings) / len(ratings) if ratings else 0

        return {
            "period": period,
            "total_sessions": total,
            "completed_sessions": len(completed),
            "completion_rate": round(len(completed) / total * 100, 1) if total > 0 else 0,
            "total_duration_minutes": total_duration,
            "average_session_duration": round(total_duration / len(completed), 1) if completed else 0,
            "session_types_breakdown": session_types,
            "average_effort_rating": round(avg_effort, 1),
            "recent_sessions": [
                {
                    "id": d.get("_id") or d.get("id"),
                    "title": d["title"],
                    "date": d["scheduled_at"].isoformat() if d.get("scheduled_at") else None,
                    "status": d["status"],
                    "duration": d.get("duration_minutes"),
                }
                for d in docs[:5]
            ],
        }

    async def get_analytics(
        self,
        user_id: str,
        session_type: Optional[str] = None,
        period: str = "month",
    ) -> dict:
        sessions = get_collection("training_sessions")
        cutoff = self._get_period_cutoff(period)

        query: dict = {"user_id": user_id, "scheduled_at": {"$gte": cutoff}}
        if session_type:
            query["session_type"] = session_type

        docs = []
        async for doc in sessions.find(query).sort("scheduled_at", 1):
            docs.append(doc)

        weekly: Dict[str, int] = {}
        focus_areas: Dict[str, int] = {}
        for d in docs:
            if d.get("scheduled_at"):
                wk = d["scheduled_at"].strftime("%Y-W%U")
                weekly[wk] = weekly.get(wk, 0) + 1
            for area in (d.get("focus_areas") or []):
                focus_areas[area] = focus_areas.get(area, 0) + 1

        completed = [d for d in docs if d["status"] == SessionStatus.COMPLETED.value]

        return {
            "period": period,
            "session_type": session_type,
            "total_sessions": len(docs),
            "completed_sessions": len(completed),
            "weekly_distribution": weekly,
            "focus_areas_frequency": focus_areas,
            "performance_metrics": {
                "consistency": round(len(completed) / len(docs) * 100, 1) if docs else 0,
                "improvement_trend": self._calc_trend(docs),
                "intensity_data": self._calc_intensity(docs),
            },
        }

    async def get_recommendations(self, user_id: str) -> dict:
        sessions = get_collection("training_sessions")
        cutoff = datetime.utcnow() - timedelta(days=30)

        docs = []
        async for doc in sessions.find(
            {"user_id": user_id, "scheduled_at": {"$gte": cutoff}}
        ).sort("scheduled_at", -1).limit(10):
            docs.append(doc)

        session_types = [d.get("session_type", "practice") for d in docs]
        last_type = session_types[0] if session_types else "practice"

        suggestions = {
            "practice": "technique",
            "technique": "tactical",
            "tactical": "fitness",
            "fitness": "practice",
            "match_prep": "recovery",
            "recovery": "technique",
        }
        next_type = suggestions.get(last_type, "practice")

        focus_counts: Dict[str, int] = {}
        for d in docs:
            for area in (d.get("focus_areas") or []):
                focus_counts[area] = focus_counts.get(area, 0) + 1

        all_areas = ["forehand", "backhand", "serve", "volley", "footwork", "return", "mental"]
        weak_areas = [a for a in all_areas if focus_counts.get(a, 0) < 2]

        return {
            "next_session_type": next_type,
            "weak_areas": weak_areas[:3],
            "total_recent": len(docs),
            "suggestions": [
                f"Foque em treinos de {next_type} na proxima sessao",
                f"Areas menos praticadas: {', '.join(weak_areas[:3]) if weak_areas else 'nenhuma identificada'}",
                "Mantenha variedade nos tipos de treino para desenvolvimento equilibrado",
            ],
            "weekly_plan": {
                "monday": "Tecnica - saque e voleio",
                "tuesday": "Fitness - cardio e agilidade",
                "wednesday": "Simulacao de partida",
                "thursday": "Recuperacao e flexibilidade",
                "friday": "Exercicios taticos",
                "saturday": "Partida ou jogo competitivo",
                "sunday": "Descanso ou pratica leve",
            },
        }

    async def get_calendar(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        sessions = get_collection("training_sessions")

        start_dt = datetime.fromisoformat(start_date) if start_date else datetime.utcnow() - timedelta(days=30)
        end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow() + timedelta(days=30)

        query = {
            "user_id": user_id,
            "scheduled_at": {"$gte": start_dt, "$lte": end_dt},
        }

        events = []
        async for doc in sessions.find(query).sort("scheduled_at", 1):
            finished = doc.get("finished_at")
            sched = doc.get("scheduled_at")
            events.append({
                "id": str(doc["_id"]),
                "title": doc["title"],
                "start": sched.isoformat() if sched else None,
                "end": (finished or (sched + timedelta(hours=2))).isoformat() if sched else None,
                "type": doc.get("session_type"),
                "status": doc["status"],
                "coach": doc.get("coach_name"),
                "description": doc.get("description"),
            })

        statuses = [e["status"] for e in events]
        return {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "events": events,
            "summary": {
                "total_sessions": len(events),
                "completed": statuses.count(SessionStatus.COMPLETED.value),
                "planned": statuses.count(SessionStatus.PLANNED.value),
                "in_progress": statuses.count(SessionStatus.IN_PROGRESS.value),
            },
        }

    # --- Helpers ---

    def _get_period_cutoff(self, period: str) -> datetime:
        now = datetime.utcnow()
        periods = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365,
        }
        days = periods.get(period, 30)
        return now - timedelta(days=days)

    def _calc_trend(self, sessions: list) -> str:
        if len(sessions) < 3:
            return "insufficient_data"
        recent = [s.get("effort_rating") for s in sessions[-5:] if s.get("effort_rating")]
        earlier = [s.get("effort_rating") for s in sessions[:-5] if s.get("effort_rating")]
        if not recent or not earlier:
            return "insufficient_data"
        r_avg = sum(recent) / len(recent)
        e_avg = sum(earlier) / len(earlier)
        if r_avg > e_avg + 0.5:
            return "improving"
        elif r_avg < e_avg - 0.5:
            return "declining"
        return "stable"

    def _calc_intensity(self, sessions: list) -> list:
        data = []
        for s in sessions:
            if s.get("intensity_level") and s.get("scheduled_at"):
                data.append({
                    "date": s["scheduled_at"].isoformat(),
                    "intensity": s["intensity_level"],
                })
        return data

    async def get_player_recommendations(
        self,
        player_id: str,
        focus_area: Optional[str] = None,
        period: str = "month",
    ) -> dict:
        """
        Gera recomendacoes personalizadas de treino com IA baseadas em historico de performance.

        Args:
            player_id: ID do jogador
            focus_area: Area de foco especifica (serve, return, consistency, break_points, unforced_errors)
            period: Periodo de analise (week, month, quarter, year)

        Returns:
            Dict com recomendacoes, exercicios sugeridos, plano semanal e insights de IA
        """
        logger.info("Gerando recomendacoes de treino", player_id=player_id, focus_area=focus_area)

        # Obter recomendacoes baseadas em analytics/IA
        ai_recommendations = await self.analytics_service.get_recommendations(
            player_id=player_id,
            period=period
        )

        # Se foi especificada uma area de foco, filtrar recomendacoes
        if focus_area:
            filtered_weaknesses = [
                w for w in ai_recommendations.get("weaknesses", [])
                if focus_area.lower() in w.get("area", "").lower()
            ]
            filtered_exercises = [
                e for e in ai_recommendations.get("suggested_exercises", [])
                if focus_area.lower() in e.get("focus", "").lower()
            ]

            if filtered_weaknesses:
                ai_recommendations["weaknesses"] = filtered_weaknesses
            if filtered_exercises:
                ai_recommendations["suggested_exercises"] = filtered_exercises

        # Mapear exercicios sugeridos para drill types existentes
        drills = get_collection("drill_types")
        available_drills = []
        async for drill in drills.find({}):
            available_drills.append(drill)

        # Criar plano semanal de treinos
        weekly_plan = self._generate_weekly_training_plan(
            ai_recommendations,
            available_drills,
            focus_area
        )

        # Gerar insights adicionais
        insights = self._generate_training_insights(ai_recommendations, focus_area)

        return {
            "player_id": player_id,
            "focus_area": focus_area,
            "analysis_period": period,
            "weaknesses": ai_recommendations.get("weaknesses", []),
            "strengths": ai_recommendations.get("strengths", []),
            "suggested_exercises": ai_recommendations.get("suggested_exercises", []),
            "focus_areas": ai_recommendations.get("focus_areas", []),
            "improvement_plan": ai_recommendations.get("improvement_plan", {}),
            "weekly_training_plan": weekly_plan,
            "ai_insights": insights,
            "priority_recommendation": ai_recommendations.get("priority_recommendation", "continue_current_training"),
            "estimated_improvement_time": ai_recommendations.get("estimated_improvement_time", "4-6 weeks"),
            "next_steps": ai_recommendations.get("next_steps", []),
        }

    def _generate_weekly_training_plan(
        self,
        recommendations: dict,
        available_drills: list,
        focus_area: Optional[str] = None,
    ) -> dict:
        """Gera um plano semanal de treinos baseado nas recomendacoes de IA"""

        weaknesses = recommendations.get("weaknesses", [])
        suggested_exercises = recommendations.get("suggested_exercises", [])

        # Estrutura base do plano semanal
        plan = {
            "monday": {
                "focus": "Tecnica e Fundamentos",
                "duration_minutes": 90,
                "drills": [],
                "intensity": "medium",
            },
            "tuesday": {
                "focus": "Condicionamento Fisico",
                "duration_minutes": 60,
                "drills": [],
                "intensity": "high",
            },
            "wednesday": {
                "focus": "Pratica Tatica",
                "duration_minutes": 90,
                "drills": [],
                "intensity": "medium",
            },
            "thursday": {
                "focus": "Recuperacao e Trabalho Mental",
                "duration_minutes": 45,
                "drills": [],
                "intensity": "low",
            },
            "friday": {
                "focus": "Pontos Fracos Identificados",
                "duration_minutes": 90,
                "drills": [],
                "intensity": "high",
            },
            "saturday": {
                "focus": "Simulacao de Partida",
                "duration_minutes": 120,
                "drills": [],
                "intensity": "high",
            },
            "sunday": {
                "focus": "Descanso ou Pratica Leve",
                "duration_minutes": 30,
                "drills": [],
                "intensity": "low",
            },
        }

        # Mapear areas fracas para categorias de drill
        category_mapping = {
            "serve": "serve",
            "return": "return",
            "consistency": "technique",
            "unforced_errors": "tactical",
            "break_points": "mental",
            "footwork": "footwork",
            "volley": "volley",
        }

        # Adicionar drills especificos para areas fracas
        primary_weakness = weaknesses[0] if weaknesses else None

        if primary_weakness:
            weak_area = primary_weakness.get("area", "")
            target_category = category_mapping.get(weak_area, "technique")

            # Encontrar drills relevantes
            relevant_drills = [
                d for d in available_drills
                if d.get("category") == target_category
            ]

            # Distribuir drills pela semana
            if relevant_drills:
                # Segunda: 2 drills de tecnica
                plan["monday"]["drills"] = [
                    {
                        "drill_type_id": d["_id"],
                        "name": d["name"],
                        "duration_minutes": d.get("duration_minutes", 20),
                        "category": d.get("category"),
                    }
                    for d in relevant_drills[:2]
                ]

                # Sexta: Foco nos pontos fracos (3 drills)
                plan["friday"]["drills"] = [
                    {
                        "drill_type_id": d["_id"],
                        "name": d["name"],
                        "duration_minutes": d.get("duration_minutes", 20),
                        "category": d.get("category"),
                    }
                    for d in relevant_drills[:3]
                ]

        # Terça: Fitness drills
        fitness_drills = [d for d in available_drills if d.get("category") == "fitness"]
        if fitness_drills:
            plan["tuesday"]["drills"] = [
                {
                    "drill_type_id": d["_id"],
                    "name": d["name"],
                    "duration_minutes": d.get("duration_minutes", 15),
                    "category": "fitness",
                }
                for d in fitness_drills[:2]
            ]

        # Quarta: Tactical drills
        tactical_drills = [d for d in available_drills if d.get("category") == "tactical"]
        if tactical_drills:
            plan["wednesday"]["drills"] = [
                {
                    "drill_type_id": d["_id"],
                    "name": d["name"],
                    "duration_minutes": d.get("duration_minutes", 25),
                    "category": "tactical",
                }
                for d in tactical_drills[:2]
            ]

        # Quinta: Mental drills
        mental_drills = [d for d in available_drills if d.get("category") == "mental"]
        if mental_drills:
            plan["thursday"]["drills"] = [
                {
                    "drill_type_id": d["_id"],
                    "name": d["name"],
                    "duration_minutes": d.get("duration_minutes", 20),
                    "category": "mental",
                }
                for d in mental_drills[:1]
            ]

        return plan

    def _generate_training_insights(
        self,
        recommendations: dict,
        focus_area: Optional[str] = None,
    ) -> dict:
        """Gera insights adicionais baseados nas recomendacoes de IA"""

        weaknesses = recommendations.get("weaknesses", [])
        strengths = recommendations.get("strengths", [])

        insights = {
            "summary": "",
            "key_priorities": [],
            "expected_outcomes": [],
            "motivation_tips": [],
        }

        # Resumo geral
        if weaknesses:
            primary_weakness = weaknesses[0]["area"]
            insights["summary"] = (
                f"Analise identificou {len(weaknesses)} areas de melhoria. "
                f"Prioridade principal: {primary_weakness}. "
            )
        else:
            insights["summary"] = "Performance esta equilibrada. Foque em manter consistencia e evoluir taticamente."

        if strengths:
            insights["summary"] += f" Pontos fortes: {', '.join(strengths[:2])}."

        # Prioridades-chave
        for w in weaknesses[:3]:
            insights["key_priorities"].append({
                "area": w["area"],
                "current": w["current_value"],
                "target": w["target_value"],
                "priority": w["severity"],
            })

        # Resultados esperados
        if weaknesses:
            insights["expected_outcomes"] = [
                f"Melhoria de {weaknesses[0]['area']} em 10-15% nas proximas 2 semanas",
                f"Alcançar meta de {weaknesses[0]['target_value']} em {weaknesses[0]['metric']} em 4-6 semanas",
                "Aumento geral de consistencia e confianca em quadra",
            ]
        else:
            insights["expected_outcomes"] = [
                "Manter nivel atual de performance",
                "Expandir repertorio tatico",
                "Melhorar adaptabilidade em diferentes superficies",
            ]

        # Dicas de motivacao
        insights["motivation_tips"] = [
            "Foco em progresso incremental, nao perfeicao",
            "Celebre pequenas vitorias em cada treino",
            "Mantenha um diario de treino para acompanhar evolucao",
            "Visualize sucessos antes de cada sessao",
        ]

        return insights
