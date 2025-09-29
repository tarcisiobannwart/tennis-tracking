# Análise de Jogadores

Este documento detalha todas as métricas e análises aplicadas aos jogadores durante uma partida de tênis, incluindo estatísticas tradicionais e avançadas.

## 📊 Estatísticas Fundamentais

### Métricas Gerais
| Métrica | Descrição | Cálculo |
|---------|-----------|---------|
| **Pontos Ganhos** | Total de pontos conquistados | Soma direta |
| **% Pontos Ganhos** | Percentual de pontos ganhos | Pontos ganhos ÷ pontos totais |
| **Games Ganhos** | Total de games conquistados | Soma por set |
| **Break Points** | Chances de quebra criadas | Situações 30-40, 0-40, etc. |

## 🎾 Análise de Saque

### Estatísticas Básicas de Saque

#### Primeiro Saque
| Métrica | Descrição | Benchmark Elite |
|---------|-----------|-----------------|
| **% 1º Saque** | Primeiros saques válidos | >65% |
| **% Pontos no 1º** | Pontos ganhos no 1º saque | >75% |
| **Velocidade Média** | Velocidade média do 1º saque | >180 km/h |
| **Velocidade Máxima** | Saque mais rápido | >200 km/h |

#### Segundo Saque
| Métrica | Descrição | Benchmark Elite |
|---------|-----------|-----------------|
| **% 2º Saque** | Segundos saques válidos | >90% |
| **% Pontos no 2º** | Pontos ganhos no 2º saque | >55% |
| **Velocidade Média** | Velocidade média do 2º saque | >150 km/h |
| **Duplas Faltas** | Erros em ambos os saques | <3% |

### Estatísticas Avançadas de Saque

#### Distribuição de Saques
| Zona | Descrição | % Típico | Efetividade |
|------|-----------|----------|-------------|
| **T (Centro)** | Saque na linha central | 40% | 72% pontos ganhos |
| **Wide** | Saque aberto | 35% | 68% pontos ganhos |
| **Body** | Saque no corpo | 25% | 75% pontos ganhos |

#### Ace e Service Winners
| Métrica | Descrição | Cálculo |
|---------|-----------|---------|
| **Aces** | Saques indefensáveis | Count direto |
| **% Aces** | Aces por saque | Aces ÷ saques totais |
| **Service Winners** | Pontos ganhos até 2º golpe | Count + contexto |
| **Unreturned Serves** | Saques não devolvidos | Aces + Service Winners |

#### Efetividade por Situação
| Situação | % 1º Saque | % Pontos Ganhos |
|----------|------------|-----------------|
| **0-0 a 30-0** | 68% | 76% |
| **30-30 a Deuce** | 62% | 71% |
| **Break Point Against** | 58% | 69% |
| **Set Point** | 65% | 78% |
| **Match Point** | 60% | 74% |

## 🔄 Análise de Retorno

### Estatísticas de Retorno

#### Performance Geral
| Métrica | Descrição | Benchmark Elite |
|---------|-----------|-----------------|
| **% Retornos Válidos** | Retornos que passaram a rede | >85% |
| **% Pontos no Retorno** | Pontos ganhos no retorno | >35% |
| **Break Points Criados** | Chances de quebra por set | 3-5 por set |
| **% Break Points Convertidos** | Quebras convertidas | >40% |

#### Retorno por Tipo de Saque
| Tipo de Saque | % Retornos Válidos | % Pontos Ganhos |
|---------------|-------------------|-----------------|
| **1º Saque** | 80% | 32% |
| **2º Saque** | 92% | 55% |
| **Saque Lento (<150)** | 95% | 65% |
| **Saque Rápido (>200)** | 70% | 25% |

### Posicionamento no Retorno
| Posição | Descrição | Uso Típico |
|---------|-----------|------------|
| **Próximo** | 1-2m atrás da linha base | Vs 2º saque |
| **Normal** | 2-3m atrás da linha base | Padrão |
| **Recuado** | 3-4m atrás da linha base | Vs sacador potente |

## 🏃‍♂️ Análise de Movimento

### Métricas de Mobilidade

#### Distância e Velocidade
| Métrica | Descrição | Benchmark Elite |
|---------|-----------|-----------------|
| **Distância Total** | Metros percorridos na partida | 2-4 km |
| **Distância por Ponto** | Metros médios por ponto | 15-25m |
| **Velocidade Máxima** | Pico de velocidade de corrida | >25 km/h |
| **Aceleração Média** | Aceleração típica | 3-5 m/s² |

#### Cobertura da Quadra
| Zona | % Tempo | Efetividade |
|------|---------|-------------|
| **Centro (T)** | 40% | Base de operação |
| **Backhand Corner** | 25% | Zona defensiva |
| **Forehand Corner** | 25% | Zona de ataque |
| **Net** | 10% | Finalizações |

### Padrões de Movimento
| Padrão | Descrição | Frequência |
|--------|-----------|------------|
| **Lateral** | Movimento lado a lado | 60% |
| **Diagonal** | Movimento em diagonal | 25% |
| **Approach** | Aproximação à rede | 10% |
| **Recovery** | Volta à posição | 5% |

## 🎯 Análise de Golpes

### Estatísticas por Tipo de Golpe

#### Golpes de Fundo
| Golpe | % do Jogo | Winners | Erros | Net Clearance |
|-------|-----------|---------|--------|---------------|
| **Forehand** | 45% | 65% | 55% | 1.2m |
| **Backhand** | 35% | 25% | 35% | 1.1m |
| **Slice** | 15% | 5% | 8% | 0.8m |
| **Lob** | 5% | 5% | 2% | 3.5m |

#### Golpes na Rede
| Golpe | Success Rate | Winners | Erros |
|-------|--------------|---------|--------|
| **Volley FH** | 78% | 45% | 15% |
| **Volley BH** | 72% | 35% | 20% |
| **Overhead** | 85% | 70% | 10% |
| **Drop Volley** | 65% | 80% | 15% |

### Velocidade de Golpes
| Golpe | Velocidade Média | Velocidade Máxima |
|-------|------------------|-------------------|
| **Forehand** | 110 km/h | 150+ km/h |
| **Backhand** | 105 km/h | 140+ km/h |
| **Slice** | 85 km/h | 110 km/h |
| **Volley** | 75 km/h | 120 km/h |

## 🧠 Análise Tática

### Padrões de Jogo

#### Estilo de Jogo
| Estilo | Características | Métricas Chave |
|--------|----------------|----------------|
| **Baseline** | Jogo de fundo | Rally length >6 |
| **All-court** | Versátil | Net points >15% |
| **Serve & Volley** | Saque e rede | 1st serve >70% |
| **Counter-puncher** | Defensivo | UE <20/set |

#### Sequências de Pontos
| Sequência | % Pontos | Efetividade |
|-----------|----------|-------------|
| **0-4 golpes** | 25% | Saque dominante |
| **5-8 golpes** | 35% | Rally médio |
| **9-12 golpes** | 25% | Rally longo |
| **13+ golpes** | 15% | Guerra de resistência |

### Análise Situacional

#### Performance por Contexto
| Situação | % Pontos Ganhos | Diferença vs Média |
|----------|----------------|--------------------|
| **0-0 a 30-0** | 65% | +5% |
| **15-30 a 30-30** | 55% | -5% |
| **Deuce** | 50% | Base |
| **Break Point** | 45% | -10% |
| **Set Point** | 70% | +15% |

#### Adaptação por Set
| Set | 1º Saque % | Winners | UE | Rally Length |
|-----|------------|---------|----| -------------|
| **1º Set** | 68% | 15 | 12 | 6.2 |
| **2º Set** | 65% | 18 | 15 | 6.8 |
| **3º Set** | 62% | 12 | 18 | 7.5 |

## 📈 Métricas Avançadas

### Pressure Points Index (PPI)
```
PPI = (Break Points Faced × Weight) + (Set Points × Weight) + (Match Points × Weight)
Onde Weight varia de 1-3 baseado na importância
```

### Momentum Tracking
| Indicador | Cálculo | Interpretação |
|-----------|---------|---------------|
| **Point Streak** | Sequência de pontos ganhos | >4 = Hot streak |
| **Game Streak** | Sequência de games ganhos | >3 = Momentum |
| **Set Momentum** | Ratio de pontos no set | >60% = Controle |

### Eficiência de Energia
| Métrica | Descrição | Cálculo |
|---------|-----------|---------|
| **Points per km** | Eficiência de movimento | Pontos ÷ distância |
| **Energy Index** | Gasto energético relativo | Distância × intensidade |
| **Rally Efficiency** | Efetividade em rallies longos | Win% em rallies 9+ |

## 🔄 Comparação e Benchmarking

### Rankings de Performance
| Categoria | Top 10 | Top 50 | Top 100 |
|-----------|--------|--------|---------|
| **1º Saque %** | >70% | >65% | >60% |
| **% Pontos 1º Saque** | >80% | >75% | >70% |
| **% Break Points Saved** | >70% | >65% | >60% |
| **Winners/UE Ratio** | >1.5 | >1.2 | >1.0 |

### Evolução Temporal
- **Por período**: Comparar performance por quartos da partida
- **Por superfície**: Adaptação a diferentes pisos
- **Por oponente**: Ajustes táticos específicos
- **Por torneio**: Consistência ao longo do ano

---

**Referências**: ATP Stats, WTA Stats, ITF Analytics Guidelines, Hawk-Eye Performance Metrics