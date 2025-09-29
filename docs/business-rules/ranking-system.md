# Sistema de Ranking

Este documento detalha os sistemas de ranking utilizados no tênis profissional, incluindo distribuição de pontos, categorias de torneios e cálculo de posições.

## 🏆 Sistema ATP (Masculino)

### Estrutura de Pontuação

#### Pontos por Torneio - ATP
| Categoria | Vencedor | Final | SF | QF | R4 | R3 | R2 | R1 | Q |
|-----------|----------|-------|----|----|----|----|----|----|---|
| **Grand Slam** | 2000 | 1200 | 720 | 360 | 180 | 90 | 45 | 10 | 25 |
| **ATP Finals** | 1500* | - | - | - | - | - | - | - | - |
| **Masters 1000** | 1000 | 600 | 360 | 180 | 90 | 45 | 25 | 10 | 16 |
| **ATP 500** | 500 | 300 | 180 | 90 | 45 | 20 | 10 | 0 | 12 |
| **ATP 250** | 250 | 150 | 90 | 45 | 20 | 10 | 5 | 0 | 5 |

*ATP Finals: pontos baseados em vitórias (200 por vitória na fase de grupos + 400 SF + 500 Final)

#### Torneios Obrigatórios - ATP
| Tipo | Quantidade | Observações |
|------|-----------|-------------|
| **Grand Slams** | 4 | Australian Open, Roland Garros, Wimbledon, US Open |
| **ATP Finals** | 1 | Se qualificado (top 8) |
| **Masters 1000** | 8 | Obrigatórios (exceto 1 pode ser substituído) |
| **Best of Rest** | 6 | Melhores resultados dos demais torneios |

### Cálculo do Ranking ATP

#### Período de Validade
- **Rolling 52 weeks**: Pontos válidos por 52 semanas
- **18 torneios máximos**: Melhor combinação possível
- **Atualização semanal**: Toda segunda-feira

#### Exemplo de Cálculo
```
Jogador X - Ranking atual:
4 Grand Slams: 2000 + 720 + 360 + 180 = 3260 pontos
8 Masters 1000: 1000 + 600 + 360 + 180 + 90 + 45 + 25 + 10 = 2310 pontos
6 Best Results: 500 + 300 + 250 + 150 + 90 + 45 = 1335 pontos
Total: 6905 pontos
```

## 👩 Sistema WTA (Feminino)

### Estrutura de Pontuação

#### Pontos por Torneio - WTA
| Categoria | Vencedor | Final | SF | QF | R4 | R3 | R2 | R1 | Q |
|-----------|----------|-------|----|----|----|----|----|----|---|
| **Grand Slam** | 2000 | 1300 | 780 | 430 | 240 | 130 | 70 | 10 | 40 |
| **WTA Finals** | 1500* | - | - | - | - | - | - | - | - |
| **WTA 1000** | 1000 | 650 | 390 | 215 | 120 | 65 | 35 | 10 | 18 |
| **WTA 500** | 470 | 305 | 185 | 100 | 55 | 30 | 15 | 1 | 9 |
| **WTA 250** | 280 | 180 | 110 | 60 | 30 | 15 | 8 | 1 | 6 |

*WTA Finals: sistema similar ao ATP

#### Diferenças WTA vs ATP
| Aspecto | WTA | ATP |
|---------|-----|-----|
| **Torneios obrigatórios** | Menos rígido | 8 Masters obrigatórios |
| **Período de validade** | 52 semanas | 52 semanas |
| **Número máximo** | 16 torneios | 18 torneios |
| **Distribuição pontos** | Mais graduada | Mais concentrada no topo |

## 🌍 Sistema ITF (Desenvolvimento)

### ITF World Tennis Tour

#### Categorias de Torneios ITF
| Categoria | Prize Money | Pontos Vencedor |
|-----------|-------------|-----------------|
| **ITF W80** | $80,000 | 80 |
| **ITF W60** | $60,000 | 60 |
| **ITF W25** | $25,000 | 25 |
| **ITF W15** | $15,000 | 15 |

#### Sistema de Acesso
```
ITF World Tennis Tour
├── ITF W15/W25 (Desenvolvimento)
├── ITF W60/W80 (Transição)
├── WTA/ATP Qualifying (Acesso)
└── WTA/ATP Main Draw (Profissional)
```

### Junior Rankings

#### Pontos por Categoria Júnior
| Torneio | Grade A | Grade 1 | Grade 2 | Grade 3 | Grade 4 | Grade 5 |
|---------|---------|---------|---------|---------|---------|---------|
| **Vencedor** | 400 | 270 | 180 | 120 | 80 | 40 |
| **Final** | 280 | 189 | 126 | 84 | 56 | 28 |
| **SF** | 200 | 135 | 90 | 60 | 40 | 20 |

## 📊 Race Rankings

### ATP Race to Turin
- **Período**: Janeiro a outubro (ATP Finals)
- **Qualificação**: Top 8 se qualificam
- **Pontos**: Mesmo sistema do ranking, mas apenas torneios do ano atual

### WTA Race to WTA Finals
- **Período**: Janeiro a outubro
- **Qualificação**: Top 8 singles + top 8 duplas
- **Critérios**: Rankings de singles e duplas separados

## 🏅 Rankings Especiais

### Champions Race

#### ATP Champions Race
```python
def calculate_race_position(player_points_2024):
    """Calcula posição na corrida atual"""
    qualifying_tournaments = [
        'grand_slams', 'atp_finals', 'masters_1000',
        'best_atp_500', 'best_atp_250'
    ]
    total_points = sum(player_points_2024[tournament]
                      for tournament in qualifying_tournaments)
    return total_points
```

### Entry System Rankings

#### Direct Acceptance (DA)
- **Grand Slams**: Top 104 (32 bye para top 32)
- **Masters 1000**: Top 96 (32 bye para top 32)
- **ATP 500**: Top 32-48 (varia por torneio)
- **ATP 250**: Top 28-32 (varia por torneio)

#### Wild Cards (WC)
- **Allocation**: Organizadores decidem
- **Typical**: 4-8 por torneio
- **Criteria**: Jogadores locais, marketing, comebacks

#### Qualificação (Q)
- **Spots**: 4-16 dependendo do torneio
- **Entry**: Ranking de qualificação separado
- **Process**: Torneio eliminatório (2-3 rodadas)

## 📈 Análise de Performance

### Efficiency Metrics

#### Points per Tournament
```python
def calculate_efficiency(total_points, tournaments_played):
    return total_points / tournaments_played

# Exemplo:
# Jogador A: 6000 pontos em 20 torneios = 300 PPT
# Jogador B: 5500 pontos em 15 torneios = 367 PPT
# Jogador B é mais eficiente
```

#### Consistency Index
| Métrica | Fórmula | Interpretação |
|---------|---------|---------------|
| **Top 10 Finishes** | Finais top 10 / torneios | Consistência alta |
| **Title Conversion** | Títulos / finais | Eficiência em finais |
| **Deep Run %** | QF+ / torneios | Regularidade |

### Surface Specialists

#### Ranking por Superfície (não oficial)
| Superfície | Período | Torneios Incluídos |
|-----------|---------|-------------------|
| **Clay** | 52 semanas | Todos em saibro |
| **Hard** | 52 semanas | Todos em quadra dura |
| **Grass** | 52 semanas | Wimbledon + preparatórios |

## 🔄 Protected Rankings

### Medical Protected Ranking

#### Critérios para PR
- **Lesão**: Mínimo 6 meses afastado
- **Ranking**: Top 50 quando lesionado
- **Usage**: Máximo 9 torneios para retorno

#### Calculation
```python
def protected_ranking(injury_date, ranking_at_injury):
    """Calcula ranking protegido"""
    if ranking_at_injury <= 10:
        protected_period = 9  # meses
    elif ranking_at_injury <= 30:
        protected_period = 6
    else:
        protected_period = 4

    return {
        'ranking': ranking_at_injury,
        'valid_until': injury_date + protected_period,
        'tournaments_remaining': 9
    }
```

## 📊 Live Rankings

### Pontos Virtuais Durante Torneios

#### Cálculo em Tempo Real
```python
def live_ranking(current_points, defending_points, potential_points):
    """Atualiza ranking durante torneio"""
    return current_points - defending_points + potential_points

# Exemplo durante Wimbledon:
# Pontos atuais: 5000
# Defendendo (SF ano passado): 720
# Possível (chegou na final): 1200
# Live ranking: 5000 - 720 + 1200 = 5480
```

### Projeções de Ranking

#### Cenários Possíveis
| Resultado | Pontos Ganhos | Novo Ranking | Movimento |
|-----------|---------------|--------------|-----------|
| **Atual** | 0 | #15 | - |
| **R1** | 10 | #16 | ↓1 |
| **R2** | 45 | #14 | ↑1 |
| **QF** | 180 | #12 | ↑3 |
| **Final** | 600 | #8 | ↑7 |
| **Campeão** | 1000 | #6 | ↑9 |

## 🎯 Entry Lists e Cutoffs

### Ranking Cutoffs Típicos

#### ATP Tour (2024)
| Torneio | Direct Acceptance | Qualificação |
|---------|------------------|--------------|
| **Grand Slam** | #104 | #300 |
| **Masters 1000** | #96 | #200 |
| **ATP 500** | #32-48 | #150 |
| **ATP 250** | #28-32 | #120 |

#### Waitlist System
1. **Withdrawals**: Jogadores que desistem
2. **Next in line**: Próximo no ranking
3. **Lucky loser**: Perdedor da qualificação
4. **Special exempt**: Lesão durante torneio

---

**Referências**: ATP Official Rankings, WTA Official Rankings, ITF Regulations, Tennis Data Innovations