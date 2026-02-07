# CLAUDE.md

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com código neste repositório.

## Visão Geral do Projeto

Tennis-tracking é um projeto de visão computacional que analisa vídeos de partidas de tênis para rastrear bolas, detectar linhas da quadra e identificar jogadores. Usa modelos de deep learning (TrackNet, YOLO, Faster R-CNN) para rastreamento e análise em tempo real.

## Comandos de Desenvolvimento

### Configuração
```bash
# Instalar dependências
pip install -r requirements.txt

# Baixar pesos YOLOv3 (237MB) - OBRIGATÓRIO
wget -O Yolov3/yolov3.weights https://pjreddie.com/media/files/yolov3.weights
```

### Executando o Pipeline
```bash
# Processamento básico de vídeo
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4 --minimap=0 --bounce=0

# Com geração de minimapa (visão superior da quadra)
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4 --minimap=1 --bounce=0

# Com detecção de quique
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4 --minimap=0 --bounce=1

# Todos os recursos habilitados
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4 --minimap=1 --bounce=1
```

## Arquitetura

### Componentes Principais

1. **Rastreamento de Bola (TrackNet)**
   - Localização: `Models/tracknet.py`
   - CNN profunda que gera mapas de calor para posição da bola
   - Pesos pré-treinados: `WeightsTracknet/model.1`
   - Entrada: frames com resolução 640x360
   - Processa 3 frames consecutivos para contexto de movimento

2. **Detecção de Quadra**
   - Classe principal: `court_detector.py::CourtDetector`
   - Geometria de referência: `court_reference.py`
   - Configurações: diretório `court_configurations/`
   - Usa transformada de Hough e transformação de perspectiva

3. **Detecção de Jogadores**
   - Modelo de detecção: `detection.py::DetectionModel`
   - Usa Faster R-CNN ResNet50 para detecção de pessoas
   - Rastreamento SORT: `sort.py` para rastreamento de múltiplos objetos
   - Rastreamento específico de jogadores: `TrackPlayers/trackplayers.py`

4. **Previsão de Quique**
   - Classificador ML: `clf.pkl` (TimeSeriesForestClassifier)
   - Dados de treinamento: `bigDF.csv`, `tracking_players.csv`
   - Features: Coordenadas da bola (x,y), velocidade, features de lag de 20 frames
   - 83% de precisão em verdadeiros positivos

### Fluxo do Pipeline de Processamento

1. **Entrada de Vídeo** → Extração de frames
2. **TrackNet** → Mapas de calor da posição da bola
3. **Detecção de Quadra** → Identificação de linhas e perspectiva da quadra
4. **Detecção de Jogadores** → Caixas delimitadoras de pessoas (filtra gandulas/espectadores)
5. **Rastreamento SORT** → IDs consistentes de jogadores entre frames
6. **Detecção de Quique** → Previsão de ponto de quique baseada em ML
7. **Visualização** → Sobrepor dados de rastreamento nos frames
8. **Saída de Vídeo** → Vídeo reconstruído com anotações

### Dependências Principais

- **Deep Learning**: TensorFlow 2.6.0, PyTorch 1.9.0+cu102
- **Visão Computacional**: OpenCV 4.1.2.30, scikit-image 0.18.3
- **Rastreamento**: filterpy 1.4.5 (filtro de Kalman), algoritmo SORT
- **Séries Temporais**: sktime 0.8.0 (previsão de quique)
- **GPU**: CUDA 10.2 necessário para performance otimizada

### Restrições Importantes

- **Performance**: ~16 minutos para processar vídeo de 15 segundos
- **Requisitos de Entrada**: Apenas vídeos de partidas oficiais (sem comerciais/intervalos)
- **Arquivo Faltante**: Deve baixar `Yolov3/yolov3.weights` separadamente (237MB)
- **Memória GPU**: Requer VRAM significativa para inferência do modelo

### Padrões de Estrutura de Arquivos

- **Modelos**: Arquiteturas de redes neurais em `Models/`
- **Pesos**: Pesos pré-treinados em `WeightsTracknet/` e `Yolov3/`
- **Entrada/Saída**: `VideoInput/` para vídeos fonte, `VideoOutput/` para resultados
- **Dados da Quadra**: `court_configurations/` para diferentes tipos de quadra
- **Dados de Treinamento**: Arquivos CSV no diretório raiz

### Notas de Desenvolvimento

- Sem framework de testes formal - verificar mudanças com vídeos de exemplo
- Pipeline de processamento em `predict_video.py` orquestra todos os componentes
- Detecção de quadra pode precisar ajustes para diferentes ângulos de câmera
- Detecção de jogadores filtra baseada na proximidade da quadra para excluir espectadores

---

## 🤖 Agentes Customizados

### Agentes Globais Recomendados

Para trabalhar com tennis-tracking (Computer Vision + Deep Learning), os seguintes agentes globais do Claude Code são recomendados:

#### Python Development (Computer Vision + ML)
- **python-backend-developer**: Desenvolvimento Python geral
- **python-ml-ai-specialist**: Deep Learning, modelos de visão computacional (TrackNet, YOLO, Faster R-CNN)
- **python-multi-db-orm**: Processamento de dados com Pandas/NumPy

#### Testing & Quality
- **testing-engineer**: Criar testes com vídeos de exemplo, validação de precisão
- **implementation-verifier**: Validar pipeline end-to-end
- **standards-compliance-validator**: Garantir padrões de código Python

#### Documentation
- **spec-writer**: Especificações de features e algoritmos
- **doc-revisor**: Revisão de documentação técnica

### Agentes Locais

Este projeto não possui agentes locais customizados no momento. Todos os agentes são globais.

---

## 📊 Agent Coordination (Workflows Comuns)

### 1. Novo Modelo de Detecção/Tracking

```
python-ml-ai-specialist → Analisar requisitos do modelo
↓
python-backend-developer → Implementar em Models/
↓
python-ml-ai-specialist → Treinar modelo (se necessário)
↓
python-backend-developer → Integrar em predict_video.py
↓
testing-engineer → Validar com vídeos de teste (precisão, FPS)
↓
implementation-verifier → Validar pipeline completo
```

### 2. Melhorar Detecção de Quadra

```
spec-writer → Documentar problemas atuais e requisitos
↓
python-ml-ai-specialist → Analisar algoritmo de Hough e transformação de perspectiva
↓
python-backend-developer → Implementar melhorias em court_detector.py
↓
testing-engineer → Validar com diferentes ângulos de câmera
```

### 3. Otimização de Performance

```
python-ml-ai-specialist → Analisar gargalos (GPU, CPU, I/O)
↓
python-backend-developer → Implementar otimizações (batch processing, async, etc)
↓
testing-engineer → Medir FPS e tempo de processamento
↓
implementation-verifier → Validar que precisão não foi afetada
```

### 4. Nova Feature de Análise

```
spec-writer → Documentar feature (ex: análise de trajetória, estatísticas)
↓
python-ml-ai-specialist → Projetar algoritmo
↓
python-backend-developer → Implementar em scripts/
↓
testing-engineer → Validar com dados reais
↓
doc-revisor → Documentar uso e interpretação
```

---

## 📏 Standards Compliance

### Referência aos Padrões Globais

Este projeto segue os padrões globais definidos em `~/.claude/CLAUDE.md`:

- **Estrutura de Código**: Organizado por tipo (Models/, scripts/, dados em VideoInput/VideoOutput/)
- **Convenções de Nomenclatura**: snake_case para Python
- **Type Hints**: Usar quando possível (especialmente em funções públicas)
- **Docstrings**: Google style para funções e classes

### Convenções Python (Computer Vision)

```python
# Imports organizados
import cv2
import numpy as np
import torch
from Models.tracknet import TrackNet

# Type hints
def detect_ball(frame: np.ndarray) -> tuple[int, int]:
    """
    Detecta posição da bola no frame.

    Args:
        frame: Frame do vídeo (numpy array)

    Returns:
        Tupla (x, y) com coordenadas da bola
    """
    pass

# Comentários em algoritmos complexos
# Aplicar transformada de Hough para detectar linhas da quadra
lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=50)
```

---

## 🎯 Quick Commands

```bash
# Setup inicial
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
wget -O Yolov3/yolov3.weights https://pjreddie.com/media/files/yolov3.weights

# Processamento básico
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4

# Com todos os recursos
python3 predict_video.py --input_video_path=VideoInput/video.mp4 --output_video_path=VideoOutput/output.mp4 --minimap=1 --bounce=1

# Limpar outputs
rm -rf VideoOutput/*.mp4
```

---

## 📚 Documentação Adicional

- **README**: Instruções de setup e uso
- **Pesos de Modelos**:
  - TrackNet: `WeightsTracknet/model.1`
  - YOLOv3: `Yolov3/yolov3.weights` (download separado)
- **Dados de Treinamento**: `bigDF.csv`, `tracking_players.csv`
- **Configurações de Quadra**: `court_configurations/`

---

## ⚠️ Considerações de Performance

- **Tempo de Processamento**: ~16 minutos para vídeo de 15 segundos
- **GPU**: CUDA 10.2 necessário para performance otimizada
- **Memória**: Requer VRAM significativa para inferência dos modelos
- **Entrada**: Apenas vídeos de partidas oficiais (sem comerciais/intervalos)

---

**Última Atualização**: 28 de outubro de 2025
**Versão**: 2.0 (Adicionado seção de agentes)