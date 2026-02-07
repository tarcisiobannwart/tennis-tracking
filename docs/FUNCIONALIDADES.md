# Levantamento de Funcionalidades - Tennis Tracking

## Visao Geral do Sistema

Sistema completo de analise de partidas de tenis usando visao computacional e deep learning. Composto por 8 modulos principais que cobrem desde a deteccao visual ate a interface web interativa.

---

## Modulo 1: Visao Computacional (Computer Vision)

**Diretorio:** `src/computer_vision/`

### 1.1 Deteccao de Bola (BallDetector)
- **Arquivo:** `src/computer_vision/detection/ball_detector.py`
- **Modelo:** TrackNet (CNN profunda)
- **Funcionalidades:**
  - Deteccao da posicao da bola em cada frame via heatmap
  - Preprocessamento de frames (resize 640x360, normalizacao)
  - Processamento de predicao em heatmap (256 classes)
  - Deteccao de circulos via Hough Transform
  - Historico de trajetoria (queue de 8 posicoes)
  - Calculo de velocidade da bola (pixels/segundo)
  - Taxa de confianca de deteccao
  - Desenho de trajetoria no frame
  - Estatisticas de deteccao (total, sucesso, taxa)
  - Reset para nova analise

### 1.2 Deteccao de Quadra (CourtDetector)
- **Arquivo:** `src/computer_vision/detection/court_detector.py`
- **Funcionalidades:**
  - Binarizacao de imagem para destacar linhas brancas (threshold 200)
  - Filtragem morfologica de pixels (contraste vertical/horizontal)
  - Deteccao de linhas via Transformada de Hough
  - Classificacao de linhas (horizontais vs verticais)
  - Merge de linhas duplicadas
  - Calculo de homografia (quadra referencia -> frame)
  - Score de confianca da transformacao
  - Rastreamento temporal da quadra entre frames
  - Overlay da quadra sobre o frame
  - Localizacao de linhas importantes (baseline, net, linhas laterais, etc.)
  - Suporte a multiplas configuracoes de quadra
  - Deteccao automatica de movimento de camera com re-deteccao

### 1.3 Deteccao de Jogadores (PlayerDetector/DetectionModel)
- **Arquivo:** `src/computer_vision/detection/player_detector.py`
- **Modelo:** Faster R-CNN ResNet50 (pre-treinado COCO)
- **Funcionalidades:**
  - Deteccao de jogador 1 (inferior/mais proximo da camera) via ROI
  - Deteccao de jogador 2 (superior) via metade superior da quadra
  - Rastreamento SORT para multiplos objetos (Kalman + Hungarian)
  - Filtragem de espectadores/gandulas usando mascara da quadra
  - Selecao por maior bounding box (deteccao inicial)
  - Rastreamento por proximidade (frames subsequentes)
  - Calculo de posicao dos pes via transformacao inversa
  - Suavizacao de posicoes (Savitzky-Golay filter)
  - Discriminacao de jogador 2 por distancia de movimento
  - Criacao de visao top-view (minimap) da partida
  - Interpolacao de coordenadas faltantes
  - Remocao de outliers na trajetoria

### 1.4 Rastreamento SORT
- **Arquivo:** `src/computer_vision/tracking/sort/sort.py`
- **Funcionalidades:**
  - Filtro de Kalman para predicao de posicao
  - Algoritmo Hungaro para associacao de deteccoes
  - Manutencao de IDs consistentes entre frames
  - Configuravel: max_age, min_hits, iou_threshold

### 1.5 Modelo TrackNet
- **Arquivo:** `src/computer_vision/models/tracknet.py`
- **Funcionalidades:**
  - Arquitetura CNN para geracao de heatmaps de bola
  - Entrada: 3 frames consecutivos (640x360)
  - Saida: Mapa de calor de probabilidade
  - Pesos pre-treinados: `WeightsTracknet/model.1`

---

## Modulo 2: Controle de Jogo (Game Control)

**Diretorio:** `src/game_control/`

### 2.1 Match Manager
- **Arquivo:** `src/game_control/match_manager.py`
- **Funcionalidades:**
  - Iniciar/pausar/resumir partida
  - Adicionar pontos com tipo (ace, winner, error, fault, etc.)
  - Sistema de callbacks para eventos (match_started, point_scored, game_won, set_won, match_completed)
  - Deteccao de break point e match point
  - Atualizacao de posicao de jogadores
  - Consulta de pontuacao atual (string e dict)
  - Estatisticas completas da partida
  - Eventos recentes com limite configuravel
  - Calculo de duracao da partida
  - Exportacao completa de dados da partida

### 2.2 Modelos de Dominio
- **Player** (`src/game_control/models/player.py`): Informacoes do jogador, posicao, estatisticas
- **Match** (`src/game_control/models/match.py`): Estado da partida, formato (best of 3/5), pontuacao
- **Court** (`src/game_control/models/court.py`): Geometria e configuracao da quadra

---

## Modulo 3: Pontuacao (Scoring)

**Diretorio:** `src/scoring/`

### 3.1 Score Manager
- **Arquivo:** `src/scoring/score_manager.py`
- **Funcionalidades:**
  - Regras oficiais ATP/WTA de pontuacao
  - Placar visual (Scoreboard) com estilos configuraves
  - Nomes abreviados automaticos (ex: "R. FEDERER")
  - Historico completo de pontos (PointHistory)
  - Classificacao de pontos: ace, winner, unforced_error, forced_error, double_fault, service_winner, return_winner
  - Deteccao automatica de break point, set point, match point
  - Situacao do game (deuce, advantage, tiebreak)
  - Dados otimizados para transmissao ao vivo (live score)
  - Cache de estatisticas com invalidacao (30s)
  - Estatisticas por set: pontos, duracao, momentos-chave
  - Exportacao completa de dados de pontuacao

### 3.2 Modelos
- **Scoreboard** (`src/scoring/models/scoreboard.py`): Display visual do placar
- **PointHistory** (`src/scoring/models/point_history.py`): Historico e tipos de pontos

---

## Modulo 4: Analytics (Analise de Performance)

**Diretorio:** `src/analytics/`

### 4.1 Performance Analyzer
- **Arquivo:** `src/analytics/performance_analyzer.py`
- **Funcionalidades:**
  - Calculo de eficiencia do jogador (winners vs errors)
  - Calculo de consistencia (taxa de erro)
  - Analise de capacidade sob pressao (break points)
  - Analise de movimento: distancia, velocidade media/maxima, cobertura da quadra
  - Calculo de momentum (tendencia positiva/negativa/neutra)
  - Comparacao de jogadores (aces, winners, errors, pontos)
  - Analise de tendencias: saque, rallies, posicionamento
  - Metricas-chave: eficiencia, consistencia, dominancia
  - Identificacao de pontos fortes e fracos
  - Identificacao de padroes de jogo
  - Timeline de performance por set
  - Recomendacoes para jogadores
  - Cache de analises com duracao configuravel

---

## Modulo 5: Eventos (Events)

**Diretorio:** `src/events/`

### 5.1 Event Manager
- **Arquivo:** `src/events/event_manager.py`
- **Funcionalidades:**
  - 17 tipos de eventos: ace, winner, error, fault, break_point, game/set/match_won, deuce, advantage, tiebreak, challenge, time_violation, medical_timeout
  - Sistema de prioridade (LOW, NORMAL, HIGH, CRITICAL)
  - Callbacks por tipo de evento
  - Deteccao automatica de eventos situacionais (break point, deuce, advantage)
  - Classificacao automatica de pontos em eventos
  - Geracao de descricoes de eventos em portugues
  - Determinacao automatica de prioridade
  - Consulta de eventos recentes com filtro por tipo
  - Estatisticas de eventos (contagem por tipo, por jogador, alta prioridade)
  - Calculo de eventos por minuto
  - Exportacao completa de eventos

---

## Modulo 6: Backend API (FastAPI)

**Diretorio:** `backend/app/`

### 6.1 Autenticacao (Auth)
- **Arquivo:** `backend/app/core/auth.py`
- **Funcionalidades:**
  - Autenticacao JWT
  - Registro de usuarios
  - Login/Logout
  - Roles: admin, player, viewer

### 6.2 API de Jogadores
- **Arquivo:** `backend/app/api/routes/players.py`
- **Endpoints (10):**
  - `GET /players/` - Listar jogadores com filtros (busca, pais, nivel, ativo)
  - `GET /players/{id}` - Perfil do jogador com estatisticas
  - `POST /players/` - Criar jogador
  - `PUT /players/{id}` - Atualizar jogador
  - `DELETE /players/{id}` - Deletar jogador (soft delete)
  - `GET /players/{id}/stats` - Estatisticas detalhadas (periodo, superficie)
  - `GET /players/{id}/matches` - Partidas do jogador
  - `GET /players/{id}/recent-form` - Forma recente (W/L)
  - `GET /players/{id}/head-to-head/{opponent}` - Confronto direto
  - `GET /players/search/ranking` - Busca por ranking

### 6.3 API de Analise ao Vivo
- **Arquivo:** `backend/app/api/routes/live_analysis.py`
- **Endpoints (7):**
  - `POST /analyze/video` - Upload de video para analise
  - `GET /analyze/status/{task_id}` - Status da analise
  - `GET /analyze/result/{task_id}` - Resultado da analise
  - `DELETE /analyze/task/{task_id}` - Cancelar analise
  - `POST /analyze/reprocess/{task_id}` - Reprocessar video
  - `GET /analyze/tasks` - Listar tarefas de analise
  - `POST /analyze/batch` - Processamento em lote (max 10 videos)

### 6.4 API de Analytics
- **Arquivo:** `backend/app/api/routes/analytics.py`
- **Endpoints (10):**
  - `GET /analytics/performance/{match_id}` - Performance da partida
  - `GET /analytics/heatmap/{match_id}` - Heatmap (posicao, golpes, saques, devolucoes)
  - `GET /analytics/comparison` - Comparacao de jogadores (periodo, superficie)
  - `GET /analytics/trends/{player_id}` - Tendencias do jogador
  - `GET /analytics/insights/{match_id}` - Insights gerados por IA
  - `GET /analytics/player-stats/{player_id}` - Estatisticas avancadas
  - `GET /analytics/rally-analysis/{match_id}` - Analise de rallies
  - `GET /analytics/serve-analysis/{match_id}` - Analise de saques
  - `GET /analytics/momentum/{match_id}` - Analise de momentum
  - `GET /analytics/court-coverage/{match_id}` - Cobertura de quadra
  - `GET /analytics/performance-forecast/{player_id}` - Previsao de performance

### 6.5 API de Treinamento
- **Arquivo:** `backend/app/api/routes/training.py`
- **Endpoints (12):**
  - `GET /training/drills` - Listar tipos de exercicios
  - `POST /training/sessions` - Criar sessao de treino
  - `GET /training/sessions` - Listar sessoes
  - `GET /training/sessions/{id}` - Detalhe da sessao
  - `PUT /training/sessions/{id}` - Atualizar sessao
  - `DELETE /training/sessions/{id}` - Deletar sessao
  - `POST /training/sessions/{id}/drills` - Adicionar exercicio
  - `PUT /training/drills/{id}` - Atualizar exercicio
  - `POST /training/sessions/{id}/start` - Iniciar sessao
  - `POST /training/sessions/{id}/finish` - Finalizar sessao
  - `GET /training/progress/{player_id}` - Progresso do treino
  - `GET /training/analytics/{player_id}` - Analytics de treino
  - `GET /training/recommendations/{player_id}` - Recomendacoes IA
  - `GET /training/calendar/{player_id}` - Calendario de treinos

### 6.6 WebSocket (Tempo Real)
- **Arquivo:** `backend/app/api/websocket/live_stream.py`
- **Funcionalidades:**
  - `ws/live/{match_id}` - Streaming ao vivo por partida
  - `ws/global` - Eventos globais do sistema
  - Connection Manager com conexoes por partida e globais
  - Envio de estado inicial da partida ao conectar
  - Ping/pong para manter conexao ativa
  - Inscricao em tipos de eventos especificos
  - Broadcast de eventos de partida, globais e progresso de analise
  - Tratamento de desconexao graceful

### 6.7 Services (Camada de Negocios)
- **Match Service** (`backend/app/services/match_service.py`): CRUD de partidas
- **Video Service** (`backend/app/services/video_service.py`): Upload, salvamento, tarefas de analise
- **Analysis Service** (`backend/app/services/analysis_service.py`): Processamento de video, limpeza
- **Player Service** (`backend/app/services/player_service.py`): CRUD de jogadores
- **Analytics Service** (`backend/app/services/analytics_service.py`): Metricas e analises
- **Training Service** (`backend/app/services/training_service.py`): Sessoes de treino

### 6.8 Modelos de Dados (Database)
- **User** - Usuarios com autenticacao
- **Player** - Jogadores com perfil e estatisticas
- **Match** - Partidas com sets e pontuacao
- **Set** - Sets da partida
- **Game** - Games do set
- **Point** - Pontos do game
- **Event** - Eventos da partida
- **Video** - Videos enviados
- **Analysis** - Resultados de analise
- **Training** - Sessoes e exercicios de treino

---

## Modulo 7: Frontend Web (React + TypeScript)

**Diretorio:** `web/src/`

### 7.1 Paginas
- **Dashboard** (`pages/Dashboard.tsx`): Visao geral do sistema
- **Login** (`pages/Login.tsx`): Autenticacao de usuarios
- **LiveAnalysis** (`pages/LiveAnalysis.tsx`): Analise em tempo real com upload de video
- **Matches** (`pages/Matches.tsx`): Lista de partidas
- **MatchDetail** (`pages/MatchDetail.tsx`): Detalhe de partida especifica
- **Players** (`pages/Players.tsx`): Gestao de jogadores
- **Analytics** (`pages/Analytics.tsx`): Dashboard de analytics
- **Training** (`pages/Training.tsx`): Gestao de treinamentos

### 7.2 Componentes
- **Layout**: Sidebar, Header, Layout principal
- **Court**: CourtView (visualizacao 2D/3D da quadra com Three.js)
- **Stats**: ScoreBoard, LiveStats, EventTimeline
- **Video**: VideoPlayer (video.js), VideoUploadModal (react-dropzone)
- **UI**: Button, Card, Input, DropdownMenu (Radix UI)
- **LanguageSelector**: Seletor de idioma (i18n)

### 7.3 State Management
- **themeStore** (Zustand): Tema claro/escuro
- **liveStore** (Zustand): Estado da analise ao vivo
- **uiStore** (Zustand): Estado da UI (sidebar, modals)

### 7.4 Services
- **api.ts**: Cliente HTTP (Axios)
- **matchService.ts**: Servicos de partida
- **websocketService.ts**: Cliente WebSocket (socket.io)

### 7.5 Internacionalizacao
- **i18n**: Suporte a multiplos idiomas (i18next)

### 7.6 Stack Tecnica
- React 18, TypeScript, Vite
- TailwindCSS + Radix UI
- React Three Fiber (3D)
- Chart.js + Recharts (graficos)
- React Query (cache de API)
- Zustand (state management)
- Video.js (player de video)
- Framer Motion (animacoes)

---

## Modulo 8: Infraestrutura (DevOps)

### 8.1 Docker
- **docker-compose.yml**: Orquestracao de servicos
  - Frontend (React/Vite - port 3000)
  - Backend (FastAPI - port 8000)
  - MongoDB (port 27017)
  - Redis (port 6380)
  - MinIO (object storage)

### 8.2 Makefile
- Comandos de build, deploy e manutencao

### 8.3 Configuracao
- **config/settings.py**: Configuracoes do sistema
- **config/paths.py**: Caminhos de arquivos
- **.env.docker**: Variaveis de ambiente

---

## Pipeline de Processamento (predict_video.py)

Fluxo completo de analise de video:

1. **Entrada** -> Leitura do video frame a frame
2. **TrackNet** -> Deteccao da posicao da bola (heatmap)
3. **CourtDetector** -> Deteccao/rastreamento de linhas da quadra
4. **PlayerDetector** -> Deteccao de jogadores (Faster R-CNN)
5. **SORT** -> Rastreamento de IDs consistentes
6. **Bounce Detection** -> Previsao de quique (TimeSeriesForest, 83% precisao)
7. **Minimap** -> Visao top-view da partida
8. **Visualizacao** -> Overlay de dados no video
9. **Saida** -> Video anotado com todas as informacoes

---

## Resumo Quantitativo

| Modulo | Funcionalidades | Endpoints API |
|--------|----------------|---------------|
| Computer Vision | 15+ | - |
| Game Control | 12+ | - |
| Scoring | 14+ | - |
| Analytics | 18+ | - |
| Events | 12+ | - |
| Backend API | - | 39+ endpoints |
| WebSocket | - | 2 endpoints |
| Frontend | 8 paginas, 12+ componentes | - |
| DevOps | 5 servicos Docker | - |

**Total estimado: 80+ funcionalidades distintas, 41+ endpoints de API**

---

*Documento gerado em: 2026-02-06*
*Versao: 1.0*
