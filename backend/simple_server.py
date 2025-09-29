#!/usr/bin/env python3
"""
Servidor FastAPI simplificado para demonstração
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Dict, List
import uvicorn
import os
import uuid
import shutil

# Criar aplicação FastAPI
app = FastAPI(
    title="Tennis Tracking API",
    description="API para análise de tênis com visão computacional",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados simulados
matches_db = {
    "1": {
        "id": "1",
        "player1": {
            "id": "1",
            "name": "Roger Federer",
            "country": "Switzerland",
            "ranking": 10
        },
        "player2": {
            "id": "2",
            "name": "Rafael Nadal",
            "country": "Spain",
            "ranking": 4
        },
        "score": "6-4, 6-2",
        "status": "completed",
        "date": "2024-09-28",
        "tournament": "ATP Masters",
        "round": "Final",
        "surface": "hard",
        "duration": "2h 15m",
        "location": "Miami, USA"
    },
    "2": {
        "id": "2",
        "player1": {
            "id": "3",
            "name": "Novak Djokovic",
            "country": "Serbia",
            "ranking": 1
        },
        "player2": {
            "id": "4",
            "name": "Carlos Alcaraz",
            "country": "Spain",
            "ranking": 2
        },
        "score": "4-6, 6-3, 2-1",
        "status": "live",
        "date": "2024-09-28",
        "tournament": "Roland Garros",
        "round": "Semifinal",
        "surface": "clay",
        "duration": "1h 45m",
        "location": "Paris, France"
    }
}

players_db = {
    "1": {"id": "1", "name": "Roger Federer", "country": "Switzerland", "ranking": 10},
    "2": {"id": "2", "name": "Rafael Nadal", "country": "Spain", "ranking": 4},
    "3": {"id": "3", "name": "Novak Djokovic", "country": "Serbia", "ranking": 1},
    "4": {"id": "4", "name": "Carlos Alcaraz", "country": "Spain", "ranking": 2}
}

# Rotas básicas
@app.get("/")
async def root():
    """Página inicial da API"""
    return HTMLResponse("""
    <html>
        <head><title>Tennis Tracking API</title></head>
        <body>
            <h1>🎾 Tennis Tracking API</h1>
            <p>API para análise de partidas de tênis com IA</p>
            <ul>
                <li><a href="/docs">📖 Documentação (Swagger)</a></li>
                <li><a href="/api/matches">🏆 Listar Partidas</a></li>
                <li><a href="/api/players">👤 Listar Jogadores</a></li>
                <li><a href="/api/health">❤️ Status da API</a></li>
            </ul>
        </body>
    </html>
    """)

@app.get("/api/health")
async def health_check():
    """Verificação de saúde da API"""
    return {"status": "healthy", "message": "Tennis Tracking API is running!"}

# Rotas de partidas
@app.get("/api/matches")
async def get_matches():
    """Listar todas as partidas"""
    matches = list(matches_db.values())
    return {
        "success": True,
        "data": {
            "data": matches,
            "total": len(matches),
            "page": 1,
            "limit": len(matches),
            "hasMore": False
        }
    }

@app.get("/api/matches/live")
async def get_live_matches():
    """Listar partidas ao vivo"""
    live_matches = [match for match in matches_db.values() if match["status"] == "live"]
    return {
        "success": True,
        "data": {
            "data": live_matches,
            "total": len(live_matches),
            "page": 1,
            "limit": len(live_matches),
            "hasMore": False
        }
    }

@app.get("/api/matches/recent")
async def get_recent_matches(limit: int = 5):
    """Listar partidas recentes"""
    recent_matches = list(matches_db.values())[:limit]
    return {
        "success": True,
        "data": {
            "data": recent_matches,
            "total": len(recent_matches),
            "page": 1,
            "limit": limit,
            "hasMore": False
        }
    }

@app.get("/api/matches/{match_id}")
async def get_match(match_id: str):
    """Obter detalhes de uma partida"""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return matches_db[match_id]

@app.get("/api/matches/{match_id}/statistics")
async def get_match_statistics(match_id: str):
    """Obter estatísticas de uma partida"""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return {
        "match_id": match_id,
        "player1Stats": {
            "aces": 12,
            "winners": 25,
            "unforcedErrors": 15,
            "firstServeIn": 45,
            "firstServeAttempts": 60
        },
        "player2Stats": {
            "aces": 8,
            "winners": 18,
            "unforcedErrors": 22,
            "firstServeIn": 38,
            "firstServeAttempts": 55
        }
    }

@app.get("/api/matches/{match_id}/highlights")
async def get_match_highlights(match_id: str):
    """Obter highlights de uma partida"""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return {
        "match_id": match_id,
        "highlights": [
            {
                "timestamp": 125,
                "type": "ace",
                "description": "Ace poderoso de Federer"
            },
            {
                "timestamp": 340,
                "type": "winner",
                "description": "Winner de backhand de Nadal"
            },
            {
                "timestamp": 567,
                "type": "break_point",
                "description": "Break point convertido"
            }
        ]
    }

@app.get("/api/matches/{match_id}/stats")
async def get_match_stats(match_id: str):
    """Obter estatísticas de uma partida (legacy)"""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    return {
        "match_id": match_id,
        "aces": {"player1": 12, "player2": 8},
        "winners": {"player1": 25, "player2": 18},
        "unforced_errors": {"player1": 15, "player2": 22},
        "break_points": {"player1": "3/5", "player2": "1/3"},
        "rally_length_avg": 4.2
    }

# Rotas de jogadores
@app.get("/api/players")
async def get_players():
    """Listar todos os jogadores"""
    return {"players": list(players_db.values())}

@app.get("/api/players/{player_id}")
async def get_player(player_id: str):
    """Obter perfil de um jogador"""
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return players_db[player_id]

@app.get("/api/players/{player_id}/stats")
async def get_player_stats(player_id: str):
    """Obter estatísticas de um jogador"""
    if player_id not in players_db:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    return {
        "player_id": player_id,
        "matches_played": 45,
        "wins": 32,
        "losses": 13,
        "win_percentage": 71.1,
        "avg_aces_per_match": 8.5,
        "avg_winners_per_match": 22.3
    }

# Rota de upload de vídeo
@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload de vídeo para análise"""
    try:
        # Validar se arquivo foi enviado
        if not file or not file.filename:
            raise HTTPException(status_code=400, detail="Nenhum arquivo foi enviado")

        # Validar tipo de arquivo
        if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
            raise HTTPException(status_code=400, detail="Formato de arquivo não suportado. Use: MP4, AVI, MOV, MKV, WMV")

        # Criar diretório de upload se não existir
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Gerar ID único para a tarefa
        task_id = str(uuid.uuid4())

        # Salvar arquivo
        file_extension = os.path.splitext(file.filename)[1]
        file_path = os.path.join(upload_dir, f"{task_id}{file_extension}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "success": True,
            "data": {
                "task_id": task_id,
                "filename": file.filename,
                "file_path": file_path,
                "status": "uploaded",
                "message": "Vídeo enviado com sucesso. Análise iniciada automaticamente.",
                "analysis_url": f"/api/analyze/status/{task_id}"
            }
        }

    except Exception as e:
        print(f"Erro no upload: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

# Rota de análise (simulada)
@app.post("/api/analyze/video")
async def analyze_video():
    """Simular análise de vídeo"""
    return {
        "task_id": "abc123",
        "status": "processing",
        "message": "Análise de vídeo iniciada",
        "estimated_time": "5-10 minutos"
    }

@app.get("/api/analyze/status/{task_id}")
async def get_analysis_status(task_id: str):
    """Obter status da análise"""
    return {
        "task_id": task_id,
        "status": "completed",
        "progress": 100,
        "results": {
            "ball_detections": 1250,
            "player_detections": 2500,
            "rallies_detected": 65,
            "aces_detected": 12
        }
    }

# WebSocket simulado (rota GET para teste)
@app.get("/ws/test")
async def websocket_test():
    """Teste de funcionalidade WebSocket"""
    return {
        "message": "WebSocket endpoint disponível",
        "endpoint": "ws://localhost:8000/ws/live/{match_id}",
        "events": ["point_scored", "game_won", "set_won", "match_update"]
    }

if __name__ == "__main__":
    print("🎾 Iniciando Tennis Tracking API...")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🌐 API: http://localhost:8000")

    uvicorn.run(
        "simple_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )