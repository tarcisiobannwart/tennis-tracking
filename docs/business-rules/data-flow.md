# Fluxo de Dados e Processamento

Este documento detalha o pipeline completo de processamento de dados no sistema de análise de tênis, desde a captura de vídeo até a geração de relatórios finais.

## 🎥 Pipeline de Processamento de Vídeo

### Captura de Dados

#### Fontes de Input
| Fonte | Tipo | Frequência | Resolução |
|-------|------|------------|-----------|
| **Câmeras principais** | Vídeo HD/4K | 60-120 FPS | 1920x1080+ |
| **Câmeras Hawk-Eye** | Vídeo alta velocidade | 340 FPS | Variável |
| **Microfones ambiente** | Áudio | 48 kHz | Estéreo |
| **Sensores quadra** | Dados estruturados | 1000 Hz | N/A |

#### Pre-processamento
```python
class VideoPreprocessor:
    def __init__(self, config):
        self.fps_target = config.fps_target
        self.resolution = config.resolution
        self.calibration = config.camera_calibration

    def process_frame(self, raw_frame):
        # 1. Correção de distorção da lente
        undistorted = cv2.undistort(raw_frame, self.calibration.matrix,
                                   self.calibration.distortion)

        # 2. Correção de cor e brilho
        color_corrected = self.color_correction(undistorted)

        # 3. Estabilização de imagem
        stabilized = self.image_stabilization(color_corrected)

        # 4. Redimensionamento se necessário
        resized = cv2.resize(stabilized, self.resolution)

        return resized
```

### Sincronização Multi-câmera

#### Calibração Temporal
```python
def synchronize_cameras(camera_feeds):
    """Sincroniza múltiplas câmeras usando timestamps"""
    reference_camera = camera_feeds[0]
    sync_delays = {}

    for camera_id, feed in enumerate(camera_feeds[1:], 1):
        # Usar padrão visual para calcular delay
        delay = calculate_sync_delay(reference_camera, feed)
        sync_delays[camera_id] = delay

    return sync_delays

def calculate_sync_delay(ref_feed, target_feed):
    """Calcula delay entre câmeras usando correlação cruzada"""
    ref_pattern = extract_sync_pattern(ref_feed)
    target_pattern = extract_sync_pattern(target_feed)

    correlation = np.correlate(ref_pattern, target_pattern, mode='full')
    delay_frames = np.argmax(correlation) - len(target_pattern) + 1

    return delay_frames / ref_feed.fps  # Converter para segundos
```

## 🔍 Detecção e Rastreamento

### Pipeline de Computer Vision

#### Estágio 1: Detecção de Objetos
```python
class TennisObjectDetector:
    def __init__(self):
        self.ball_detector = YOLOv5('ball_model.pt')
        self.player_detector = YOLOv5('player_model.pt')
        self.racquet_detector = YOLOv5('racquet_model.pt')

    def detect_frame(self, frame):
        detections = {
            'ball': self.ball_detector(frame),
            'players': self.player_detector(frame),
            'racquets': self.racquet_detector(frame)
        }

        # Filtrar detecções com baixa confiança
        filtered = self.filter_low_confidence(detections, threshold=0.7)

        return filtered

    def filter_low_confidence(self, detections, threshold):
        filtered = {}
        for obj_type, dets in detections.items():
            filtered[obj_type] = [d for d in dets if d.confidence > threshold]
        return filtered
```

#### Estágio 2: Rastreamento Temporal
```python
class MultiObjectTracker:
    def __init__(self):
        self.ball_tracker = KalmanTracker()
        self.player_trackers = {}
        self.track_id_counter = 0

    def update(self, detections, timestamp):
        tracks = {}

        # Rastrear bola (único objeto)
        if detections['ball']:
            ball_track = self.ball_tracker.update(
                detections['ball'][0], timestamp
            )
            tracks['ball'] = ball_track

        # Rastrear jogadores (múltiplos objetos)
        player_tracks = self.track_players(
            detections['players'], timestamp
        )
        tracks['players'] = player_tracks

        return tracks

    def track_players(self, player_detections, timestamp):
        """Associa detecções a tracks existentes ou cria novos"""
        assignments = self.hungarian_assignment(
            self.player_trackers, player_detections
        )

        updated_tracks = {}
        for track_id, detection in assignments.items():
            if track_id in self.player_trackers:
                updated_tracks[track_id] = self.player_trackers[track_id].update(
                    detection, timestamp
                )
            else:
                # Novo track
                new_tracker = KalmanTracker()
                updated_tracks[track_id] = new_tracker.init(
                    detection, timestamp
                )

        self.player_trackers = updated_tracks
        return updated_tracks
```

### Validação de Trajetórias

#### Filtros de Física
```python
class PhysicsValidator:
    def __init__(self):
        self.gravity = 9.81  # m/s²
        self.air_resistance = 0.47  # Coeficiente da bola
        self.max_velocity = 70  # m/s (250 km/h)

    def validate_ball_trajectory(self, trajectory):
        """Valida se trajetória da bola é fisicamente possível"""
        for i in range(1, len(trajectory)):
            prev_point = trajectory[i-1]
            curr_point = trajectory[i]

            dt = curr_point.timestamp - prev_point.timestamp
            velocity = self.calculate_velocity(prev_point, curr_point, dt)

            # Verificar velocidade máxima
            if velocity.magnitude > self.max_velocity:
                return False, f"Velocidade impossível: {velocity.magnitude}"

            # Verificar aceleração (gravity + air resistance)
            if i > 1:
                prev_velocity = self.calculate_velocity(
                    trajectory[i-2], prev_point, dt
                )
                acceleration = (velocity - prev_velocity) / dt

                if abs(acceleration.y + self.gravity) > 15:  # Tolerância
                    return False, f"Aceleração não natural: {acceleration}"

        return True, "Trajetória válida"
```

## ⚡ Processamento em Tempo Real

### Arquitetura de Streaming

#### Message Queue System
```python
import asyncio
from kafka import KafkaProducer, KafkaConsumer

class TennisDataStreamer:
    def __init__(self, config):
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    async def stream_detections(self, video_feed):
        """Stream detecções em tempo real"""
        async for frame in video_feed:
            timestamp = frame.timestamp
            detections = await self.detect_objects(frame)

            # Enviar para diferentes tópicos
            await self.send_to_topic('ball_detections', {
                'timestamp': timestamp,
                'detections': detections['ball']
            })

            await self.send_to_topic('player_detections', {
                'timestamp': timestamp,
                'detections': detections['players']
            })

    async def send_to_topic(self, topic, data):
        self.producer.send(topic, data)
```

### Event-Driven Processing

#### Triggers de Eventos
```python
class EventProcessor:
    def __init__(self):
        self.event_handlers = {
            'ball_impact': self.handle_ball_impact,
            'point_start': self.handle_point_start,
            'point_end': self.handle_point_end,
            'game_end': self.handle_game_end
        }

    async def process_event(self, event):
        handler = self.event_handlers.get(event.type)
        if handler:
            await handler(event)

    async def handle_ball_impact(self, event):
        """Processa impacto da bola (raquete, solo, rede)"""
        impact_data = event.data

        if impact_data.surface == 'court':
            # Verificar se está dentro das linhas
            line_call = await self.check_line_call(impact_data.position)
            await self.emit_event('line_call', {
                'position': impact_data.position,
                'call': line_call,
                'confidence': impact_data.confidence
            })

        elif impact_data.surface == 'racquet':
            # Detectar tipo de golpe
            shot_type = await self.classify_shot(impact_data)
            await self.emit_event('shot_detected', {
                'type': shot_type,
                'player': impact_data.player_id,
                'velocity': impact_data.ball_velocity
            })
```

## 📊 Cálculo de Estatísticas

### Estatísticas em Tempo Real

#### Sistema de Contadores
```python
class LiveStatsCalculator:
    def __init__(self):
        self.match_state = MatchState()
        self.player_stats = defaultdict(PlayerStats)

    def update_stats(self, event):
        """Atualiza estatísticas baseado em eventos"""
        if event.type == 'ace':
            self.player_stats[event.player_id].aces += 1

        elif event.type == 'double_fault':
            self.player_stats[event.player_id].double_faults += 1

        elif event.type == 'winner':
            self.player_stats[event.player_id].winners += 1

        elif event.type == 'unforced_error':
            self.player_stats[event.player_id].unforced_errors += 1

    def calculate_percentage_stats(self, player_id):
        """Calcula estatísticas percentuais"""
        stats = self.player_stats[player_id]

        return {
            'first_serve_percentage': stats.first_serves_in / stats.first_serves * 100,
            'first_serve_points_won': stats.first_serve_points_won / stats.first_serves_in * 100,
            'break_points_converted': stats.break_points_won / stats.break_points_faced * 100
        }
```

### Métricas Avançadas

#### Momentum Tracking
```python
class MomentumTracker:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.point_history = []

    def update_momentum(self, point_winner, timestamp):
        """Atualiza momentum baseado no último ponto"""
        self.point_history.append({
            'winner': point_winner,
            'timestamp': timestamp
        })

        # Manter apenas janela recente
        if len(self.point_history) > self.window_size:
            self.point_history.pop(0)

    def calculate_momentum(self):
        """Calcula momentum atual (-1 a +1)"""
        if not self.point_history:
            return 0

        player_a_points = sum(1 for p in self.point_history if p['winner'] == 'A')
        total_points = len(self.point_history)

        # Normalizar para -1 a +1
        momentum = (player_a_points / total_points - 0.5) * 2

        # Aplicar peso temporal (pontos recentes valem mais)
        weights = np.exp(np.linspace(-1, 0, total_points))
        weighted_momentum = np.average(
            [1 if p['winner'] == 'A' else -1 for p in self.point_history],
            weights=weights
        )

        return weighted_momentum
```

## 💾 Armazenamento e Persistência

### Estrutura de Dados

#### Schema de Banco de Dados
```sql
-- Tabela principal de partidas
CREATE TABLE matches (
    id UUID PRIMARY KEY,
    tournament_id UUID,
    court_id UUID,
    date TIMESTAMP,
    player_a_id UUID,
    player_b_id UUID,
    final_score JSONB,
    duration_minutes INTEGER,
    surface_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Eventos da partida (granular)
CREATE TABLE match_events (
    id UUID PRIMARY KEY,
    match_id UUID REFERENCES matches(id),
    timestamp TIMESTAMP,
    event_type VARCHAR(50),
    player_id UUID,
    data JSONB,
    confidence FLOAT,
    validated BOOLEAN DEFAULT FALSE
);

-- Estatísticas por set
CREATE TABLE set_statistics (
    id UUID PRIMARY KEY,
    match_id UUID REFERENCES matches(id),
    set_number INTEGER,
    player_id UUID,
    stats JSONB
);

-- Trajetórias da bola (alta frequência)
CREATE TABLE ball_trajectories (
    id BIGSERIAL PRIMARY KEY,
    match_id UUID REFERENCES matches(id),
    timestamp TIMESTAMP,
    x_position FLOAT,
    y_position FLOAT,
    z_position FLOAT,
    velocity_x FLOAT,
    velocity_y FLOAT,
    velocity_z FLOAT,
    confidence FLOAT
);
```

### Data Lake Architecture

#### Particionamento por Tempo
```python
class DataPartitioner:
    def __init__(self, storage_backend):
        self.storage = storage_backend

    def partition_data(self, data, timestamp):
        """Particiona dados por tempo para otimizar queries"""
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        hour = timestamp.hour

        partition_path = f"tennis_data/year={year}/month={month:02d}/day={day:02d}/hour={hour:02d}"

        return self.storage.write_parquet(
            data,
            path=partition_path,
            compression='snappy'
        )

    def query_timerange(self, start_time, end_time):
        """Query eficiente usando partições"""
        partitions = self.get_partitions_in_range(start_time, end_time)

        # Parallel read das partições relevantes
        results = []
        for partition in partitions:
            partition_data = self.storage.read_parquet(partition)
            filtered = partition_data[
                (partition_data.timestamp >= start_time) &
                (partition_data.timestamp <= end_time)
            ]
            results.append(filtered)

        return pd.concat(results)
```

## 🔄 Pipeline de Análise Pós-jogo

### Processamento Batch

#### Análise Completa da Partida
```python
class PostMatchAnalyzer:
    def __init__(self):
        self.analyzers = [
            TacticalAnalyzer(),
            PerformanceAnalyzer(),
            MovementAnalyzer(),
            ShotAnalyzer()
        ]

    async def analyze_match(self, match_id):
        """Análise completa pós-partida"""
        match_data = await self.load_match_data(match_id)

        analysis_results = {}

        # Executar análises em paralelo
        tasks = []
        for analyzer in self.analyzers:
            task = asyncio.create_task(
                analyzer.analyze(match_data)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Combinar resultados
        for analyzer, result in zip(self.analyzers, results):
            analysis_results[analyzer.name] = result

        # Gerar relatório final
        report = await self.generate_report(analysis_results)

        return report

    async def generate_report(self, analysis_results):
        """Gera relatório consolidado"""
        report = {
            'summary': self.create_summary(analysis_results),
            'detailed_stats': analysis_results,
            'insights': self.extract_insights(analysis_results),
            'visualizations': await self.create_visualizations(analysis_results)
        }

        return report
```

### Cache e Otimização

#### Sistema de Cache Inteligente
```python
class AnalysisCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = {
            'live_stats': 5,      # 5 segundos
            'match_summary': 3600, # 1 hora
            'historical_data': 86400 # 1 dia
        }

    async def get_cached_analysis(self, cache_key, data_type='match_summary'):
        """Recupera análise do cache"""
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None

    async def cache_analysis(self, cache_key, data, data_type='match_summary'):
        """Armazena análise no cache"""
        ttl = self.cache_ttl.get(data_type, 3600)

        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )

    def generate_cache_key(self, match_id, analysis_type, params=None):
        """Gera chave única para cache"""
        key_parts = [f"tennis:{analysis_type}:{match_id}"]

        if params:
            param_hash = hashlib.md5(
                json.dumps(params, sort_keys=True).encode()
            ).hexdigest()[:8]
            key_parts.append(param_hash)

        return ":".join(key_parts)
```

## 📈 Monitoramento e Observabilidade

### Métricas do Sistema

#### Health Checks
```python
class SystemMonitor:
    def __init__(self):
        self.metrics = {
            'processing_latency': Histogram('processing_latency_seconds'),
            'detection_accuracy': Gauge('detection_accuracy_percentage'),
            'throughput': Counter('frames_processed_total'),
            'errors': Counter('processing_errors_total')
        }

    async def health_check(self):
        """Verifica saúde do sistema"""
        checks = {
            'camera_feeds': await self.check_camera_feeds(),
            'detection_pipeline': await self.check_detection_pipeline(),
            'database': await self.check_database(),
            'storage': await self.check_storage(),
            'processing_queue': await self.check_processing_queue()
        }

        overall_health = all(checks.values())

        return {
            'healthy': overall_health,
            'components': checks,
            'timestamp': datetime.utcnow()
        }

    async def check_detection_pipeline(self):
        """Verifica pipeline de detecção"""
        try:
            # Processar frame de teste
            test_frame = self.generate_test_frame()
            start_time = time.time()

            detections = await self.detector.detect(test_frame)

            processing_time = time.time() - start_time
            self.metrics['processing_latency'].observe(processing_time)

            # Verificar se há detecções válidas
            valid_detections = len(detections) > 0

            return valid_detections and processing_time < 0.1  # 100ms max

        except Exception as e:
            self.metrics['errors'].inc()
            logger.error(f"Detection pipeline check failed: {e}")
            return False
```

---

**Referências**: Computer Vision Pipeline Design, Real-time Sports Analytics, Apache Kafka Documentation, Redis Caching Patterns