# Nova Estrutura Proposta para Tennis Tracking

## Estrutura de Diretórios

```
tennis-tracking/
│
├── src/                              # Código fonte principal
│   ├── __init__.py
│   ├── main.py                      # Ponto de entrada principal (antigo predict_video.py)
│   │
│   ├── core/                        # Módulos principais
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Pipeline de processamento
│   │   ├── video_processor.py       # Processamento de vídeo
│   │   └── visualization.py         # Visualização e renderização
│   │
│   ├── detection/                   # Módulos de detecção
│   │   ├── __init__.py
│   │   ├── ball/                    # Detecção de bola
│   │   │   ├── __init__.py
│   │   │   ├── tracknet.py         # Modelo TrackNet
│   │   │   └── ball_detector.py    # Lógica de detecção
│   │   │
│   │   ├── court/                   # Detecção de quadra
│   │   │   ├── __init__.py
│   │   │   ├── court_detector.py   # Detector de quadra
│   │   │   └── court_reference.py  # Referências geométricas
│   │   │
│   │   └── players/                 # Detecção de jogadores
│   │       ├── __init__.py
│   │       ├── player_detector.py  # Detector de jogadores
│   │       └── person_filter.py    # Filtros (jogador vs espectador)
│   │
│   ├── tracking/                    # Módulos de rastreamento
│   │   ├── __init__.py
│   │   ├── sort/                    # Algoritmo SORT
│   │   │   ├── __init__.py
│   │   │   ├── sort.py            # Implementação SORT
│   │   │   └── kalman_filter.py   # Filtro de Kalman
│   │   │
│   │   ├── ball_tracker.py        # Rastreamento de bola
│   │   └── player_tracker.py      # Rastreamento de jogadores
│   │
│   ├── analysis/                   # Análise e predição
│   │   ├── __init__.py
│   │   ├── bounce_predictor.py    # Predição de quiques
│   │   ├── statistics.py          # Estatísticas do jogo
│   │   └── minimap_generator.py   # Geração de minimapa
│   │
│   ├── models/                     # Definições de modelos
│   │   ├── __init__.py
│   │   ├── base_model.py          # Classe base para modelos
│   │   ├── tracknet_arch.py       # Arquitetura TrackNet
│   │   └── yolo_wrapper.py        # Wrapper para YOLO
│   │
│   └── utils/                      # Utilitários
│       ├── __init__.py
│       ├── file_handler.py        # Manipulação de arquivos
│       ├── video_utils.py         # Utilitários de vídeo
│       ├── geometry.py            # Cálculos geométricos
│       └── device_utils.py        # Detecção GPU/CPU
│
├── config/                         # Configurações
│   ├── __init__.py
│   ├── settings.py                # Configurações gerais
│   ├── model_config.py           # Configurações de modelos
│   └── paths.py                  # Caminhos do sistema
│
├── data/                          # Dados e recursos
│   ├── weights/                  # Pesos dos modelos
│   │   ├── tracknet/
│   │   ├── yolo/
│   │   └── classifiers/
│   │
│   ├── court_configs/            # Configurações de quadra
│   ├── training_data/            # Dados de treinamento
│   └── samples/                  # Amostras de vídeo
│
├── tests/                        # Testes
│   ├── __init__.py
│   ├── unit/                    # Testes unitários
│   │   ├── test_ball_detection.py
│   │   ├── test_court_detection.py
│   │   └── test_player_detection.py
│   │
│   └── integration/             # Testes de integração
│       └── test_pipeline.py
│
├── scripts/                     # Scripts utilitários
│   ├── download_weights.py     # Download de pesos
│   ├── prepare_data.py        # Preparação de dados
│   └── benchmark.py           # Benchmark de performance
│
├── docs/                       # Documentação
│   ├── api/                   # Documentação da API
│   ├── guides/                # Guias de uso
│   └── architecture.md        # Arquitetura do sistema
│
├── notebooks/                  # Jupyter notebooks
│   ├── demo.ipynb            # Demonstração
│   └── training.ipynb        # Treinamento de modelos
│
├── docker/                    # Configurações Docker
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .github/                   # GitHub Actions e templates
├── requirements/              # Dependências organizadas
│   ├── base.txt              # Dependências base
│   ├── dev.txt               # Dependências de desenvolvimento
│   └── test.txt              # Dependências de teste
│
├── setup.py                  # Configuração de instalação
├── pyproject.toml           # Configuração do projeto
├── Makefile                 # Comandos make
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore

## Vantagens da Nova Estrutura

### 1. Modularidade
- Separação clara de responsabilidades
- Fácil adição de novos módulos
- Reutilização de código

### 2. Escalabilidade
- Estrutura preparada para crescimento
- Fácil adição de novos modelos/algoritmos
- Suporte para múltiplas configurações

### 3. Manutenibilidade
- Código organizado por funcionalidade
- Testes separados e organizados
- Configuração centralizada

### 4. Desenvolvimento
- Estrutura clara para novos desenvolvedores
- Separação de ambientes (dev/test/prod)
- Scripts utilitários organizados

### 5. Deployment
- Suporte Docker nativo
- Configuração via arquivos/ambiente
- Setup.py para instalação como pacote

## Plano de Migração

1. **Fase 1**: Criar estrutura de diretórios
2. **Fase 2**: Mover arquivos mantendo funcionalidade
3. **Fase 3**: Refatorar imports e dependências
4. **Fase 4**: Adicionar configuração centralizada
5. **Fase 5**: Implementar testes
6. **Fase 6**: Atualizar documentação