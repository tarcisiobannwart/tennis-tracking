# Regras de Detecção e Visão Computacional

Este documento define os critérios técnicos para detecção automática de eventos no tênis, tolerâncias permitidas e validações necessárias para garantir precisão e confiabilidade.

## 🎯 Detecção de Bola

### Critérios de Validação

#### Parâmetros Físicos da Bola
| Propriedade | Valor Oficial | Tolerância Sistema |
|-------------|---------------|-------------------|
| **Diâmetro** | 6.35-6.67 cm | ±0.5 cm |
| **Peso** | 56.0-59.4 g | N/A (visual) |
| **Cor** | Amarelo/verde fluorescente | HSV range específico |
| **Pressão** | 8.5-8.8 psi | Afeta quique |

#### Detecção Visual
| Critério | Threshold | Confidence |
|----------|-----------|------------|
| **Forma circular** | Circularidade > 0.7 | 85% |
| **Cor característica** | HSV: H(45-65), S(0.4-1.0), V(0.3-1.0) | 90% |
| **Tamanho consistente** | 15-80 pixels diâmetro | 80% |
| **Movimento suave** | Aceleração < 15 m/s² | 75% |

### Tracking Temporal

#### Continuidade de Trajetória
| Parâmetro | Valor Limite | Ação se Excedido |
|-----------|--------------|------------------|
| **Velocidade máxima** | 70 m/s (250 km/h) | Rejeitar detecção |
| **Aceleração máxima** | 25 m/s² | Verificar com câmera adicional |
| **Gap temporal** | 3 frames (0.1s) | Interpolação |
| **Mudança direção** | >90° em 1 frame | Validar impacto |

#### Filtros de Ruído
```python
# Exemplo de filtro Kalman simplificado
def filter_ball_position(previous_pos, current_detection, velocity):
    predicted_pos = previous_pos + velocity * dt
    if distance(predicted_pos, current_detection) > threshold:
        confidence *= 0.7  # Reduzir confiança
    return weighted_average(predicted_pos, current_detection)
```

## 👥 Detecção de Jogadores

### Identificação de Pessoas

#### Critérios de Classificação
| Elemento | Jogador | Não-Jogador | Confidence |
|----------|---------|-------------|------------|
| **Raquete detectada** | Obrigatório | Ausente | 95% |
| **Posição na quadra** | Dentro | Fora/arquibancada | 90% |
| **Vestimenta esportiva** | Sim | Variável | 70% |
| **Movimento atlético** | Característico | Estático/casual | 80% |

#### Validação de Jogador
```python
def validate_player(person_detection):
    score = 0
    if has_racquet(person_detection): score += 40
    if in_court_area(person_detection): score += 30
    if athletic_posture(person_detection): score += 20
    if appropriate_clothing(person_detection): score += 10
    return score >= 70  # 70% confidence threshold
```

### Diferenciação de Jogadores

#### Jogador 1 vs Jogador 2
| Método | Descrição | Reliability |
|--------|-----------|-------------|
| **Posição inicial** | Lado da quadra no saque | 95% |
| **Vestimenta** | Cor/padrão da roupa | 85% |
| **Características físicas** | Altura, build | 80% |
| **Tracking temporal** | Continuidade de movimento | 90% |

#### Casos Problemáticos
- **Cruzamento**: Quando jogadores se cruzam na rede
- **Oclusão**: Quando um jogador bloqueia o outro
- **Distância**: Em jogadas muito próximas
- **Similaridade**: Roupas/físico muito parecidos

## 🏓 Detecção de Eventos

### Impacto da Bola

#### Critérios de Impacto
| Tipo | Indicadores Visuais | Indicadores Físicos |
|------|-------------------|-------------------|
| **Quique no solo** | Achatamento da bola | Mudança brusca de direção |
| **Impacto na rede** | Deformação da rede | Parada/redução velocidade |
| **Impacto na raquete** | Proximidade raquete-bola | Mudança trajetória |
| **Impacto no corpo** | Sobreposição jogador-bola | Desvio não-raquete |

#### Precisão de Detecção
| Evento | Precision Required | Método Principal |
|--------|-------------------|------------------|
| **Linha base** | ±3.6mm | Triangulação múltiplas câmeras |
| **Linha lateral** | ±3.6mm | Hawk-Eye system |
| **Service line** | ±5mm | Análise frame-by-frame |
| **Net cord** | ±10mm | Sensor + visual |

### Validação de Linhas

#### Sistema Hawk-Eye
```python
class LineCallSystem:
    def __init__(self):
        self.cameras = 10  # Mínimo para triangulação
        self.fps = 340     # Frames por segundo
        self.precision = 3.6  # mm de precisão

    def ball_position_at_bounce(self, timestamp):
        # Triangulação 3D baseada em múltiplas câmeras
        positions = []
        for camera in self.cameras:
            pos_2d = camera.get_ball_position(timestamp)
            positions.append(self.project_to_3d(pos_2d, camera))
        return self.triangulate(positions)

    def is_ball_in(self, court_position):
        return self.court_boundaries.contains(court_position)
```

## 🎾 Detecção de Raquetes

### Características da Raquete

#### Propriedades Visuais
| Propriedade | Valor Típico | Variação |
|-------------|--------------|----------|
| **Comprimento** | 68.5 cm | ±5 cm |
| **Largura cabeça** | 25-30 cm | Variável |
| **Formato** | Oval alongado | Padrão |
| **Cor cabo** | Variada | Qualquer |
| **Cordas** | Padrão cruzado | Detectável |

#### Detecção de Swing
| Fase | Características | Indicators |
|------|----------------|------------|
| **Backswing** | Raquete para trás | Aceleração negativa |
| **Forward swing** | Movimento para frente | Aceleração positiva |
| **Impact** | Contacto com bola | Velocidade máxima |
| **Follow-through** | Finalização | Desaceleração |

### Algoritmos de Detecção

#### Template Matching
```python
def detect_racquet(frame, templates):
    best_match = None
    best_score = 0
    for template in templates:
        for scale in [0.8, 1.0, 1.2]:  # Variações de tamanho
            for rotation in range(0, 360, 15):  # Rotações
                match_score = cv2.matchTemplate(
                    frame,
                    transform(template, scale, rotation),
                    cv2.TM_CCOEFF_NORMED
                )
                if match_score > best_score:
                    best_match = (scale, rotation, location)
                    best_score = match_score
    return best_match if best_score > 0.7 else None
```

## 🔊 Detecção por Áudio

### Eventos Sonoros

#### Sons Característicos
| Evento | Frequência | Amplitude | Duração |
|--------|-----------|-----------|---------|
| **Impacto raquete-bola** | 500-2000 Hz | Alta | 50-100ms |
| **Quique no solo** | 200-800 Hz | Média | 100-200ms |
| **Net cord** | 300-1200 Hz | Baixa-média | 200-400ms |
| **Shoe squeak** | 1000-4000 Hz | Baixa | 100-300ms |

#### Sincronização Audio-Visual
```python
def sync_audio_visual(audio_event, visual_frames):
    # Compensar delay de processamento
    audio_timestamp = audio_event.timestamp - AUDIO_DELAY
    visual_timestamp = find_closest_frame(visual_frames, audio_timestamp)

    if abs(audio_timestamp - visual_timestamp) < 50:  # 50ms tolerance
        return True, visual_timestamp
    return False, None
```

## 📊 Métricas de Confiabilidade

### Thresholds de Confidence

#### Por Tipo de Detecção
| Tipo | Minimum Confidence | Preferred Confidence |
|------|-------------------|---------------------|
| **Ball detection** | 80% | 95% |
| **Player identification** | 70% | 90% |
| **Line calls** | 95% | 99% |
| **Event classification** | 75% | 85% |
| **Racquet detection** | 60% | 80% |

#### Combinação de Evidências
```python
def final_confidence(visual_conf, audio_conf, temporal_conf):
    # Weighted combination
    weights = {'visual': 0.6, 'audio': 0.2, 'temporal': 0.2}

    final = (visual_conf * weights['visual'] +
             audio_conf * weights['audio'] +
             temporal_conf * weights['temporal'])

    # Boost if all sources agree
    if all(conf > 0.8 for conf in [visual_conf, audio_conf, temporal_conf]):
        final *= 1.1

    return min(final, 1.0)
```

### Validação Cruzada

#### Múltiplas Câmeras
- **Triangulação**: Mínimo 3 câmeras para posição 3D
- **Consenso**: Maioria das câmeras deve concordar
- **Outlier detection**: Rejeitar câmeras com erro >10%

#### Temporal Consistency
- **Trajetória suave**: Sem saltos irreais
- **Física realista**: Respeitar gravidade e aerodinâmica
- **Momentum conservation**: Impactos devem conservar energia

## 🔧 Configurações do Sistema

### Parâmetros Ajustáveis

#### Sensibilidade vs Precisão
| Setting | Ball Detection | Line Calls | Event Recognition |
|---------|---------------|------------|------------------|
| **Conservative** | 95% conf | 99% conf | 90% conf |
| **Balanced** | 85% conf | 95% conf | 80% conf |
| **Aggressive** | 75% conf | 90% conf | 70% conf |

#### Condições Ambientais
| Condição | Ajustes Necessários |
|----------|-------------------|
| **Luz baixa** | Aumentar ISO, reduzir FPS |
| **Chuva** | Filtros de ruído mais agressivos |
| **Vento forte** | Aumentar tolerância trajetória |
| **Multidão barulhenta** | Reduzir peso do áudio |

### Calibração de Câmeras

#### Processo de Setup
1. **Posicionamento**: 10-14 câmeras ao redor da quadra
2. **Calibração intrínseca**: Distorção das lentes
3. **Calibração extrínseca**: Posição relativa entre câmeras
4. **Mapeamento da quadra**: Transformação 2D→3D
5. **Sincronização temporal**: Alinhamento de timestamps

#### Validação de Setup
```python
def validate_camera_setup():
    tests = [
        test_court_corners_visible(),
        test_triangulation_accuracy(),
        test_temporal_sync(),
        test_baseline_precision(),
        test_net_coverage()
    ]
    return all(tests)
```

---

**Referências**: Hawk-Eye Technical Documentation, ITF Electronic Line Calling Standards, Computer Vision for Sports Analytics Research