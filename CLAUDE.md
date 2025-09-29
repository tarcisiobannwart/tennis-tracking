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