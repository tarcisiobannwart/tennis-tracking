# Regras de Pontuação

Este documento detalha todas as regras de pontuação no tênis, incluindo variações por organização e situações especiais.

## 📊 Sistema Tradicional de Pontuação

### Pontuação por Pontos

| Pontos Ganhos | Pontuação Exibida |
|---------------|-------------------|
| 0             | 0                 |
| 1             | 15                |
| 2             | 30                |
| 3             | 40                |
| 4+            | Game (se adversário < 40) |

### Situações Especiais

#### Deuce (40-40)
- Ambos jogadores com 40 pontos
- Necessário vantagem de 2 pontos para ganhar o game
- Próximo ponto: Advantage (AD) para quem pontuar
- Se jogador com AD perder próximo ponto: volta para Deuce

#### Advantage (Vantagem)
- Jogador com 1 ponto de vantagem após Deuce
- Se pontuar novamente: ganha o game
- Se adversário pontuar: volta para Deuce

## 🎯 Tiebreak

### Tiebreak Tradicional (7 pontos)
- Ativado quando set chega a 6-6
- Primeiro a atingir 7 pontos com diferença mínima de 2
- Pontuação: 1, 2, 3, 4, 5, 6, 7...
- Se 6-6 no tiebreak: continua até diferença de 2

#### Regras de Saque no Tiebreak
| Pontos | Sacador |
|--------|---------|
| 1      | Jogador A |
| 2-3    | Jogador B |
| 4-5    | Jogador A |
| 6-7    | Jogador B |
| 8-9    | Jogador A |
| ...    | Alternando a cada 2 pontos |

### Super Tiebreak (10 pontos)
- Usado em vez de terceiro set em alguns torneios
- Primeiro a atingir 10 pontos com diferença mínima de 2
- Mesmo sistema de alternância de saque

### Tiebreak Longo (Wimbledon)
- A partir de 2019, no quinto set (ou terceiro no feminino)
- Ativado quando set chega a 12-12
- Primeiro a 7 pontos com diferença de 2

## 🏆 Variações por Organização

### ATP (Masculino)
- **Grand Slams**: Melhor de 5 sets, tiebreak no quinto set (exceto Roland Garros)
- **Masters 1000/500/250**: Melhor de 3 sets, super tiebreak no terceiro set
- **ATP Finals**: Melhor de 3 sets, super tiebreak no terceiro set

### WTA (Feminino)
- **Grand Slams**: Melhor de 3 sets, super tiebreak no terceiro set
- **WTA 1000/500/250**: Melhor de 3 sets, super tiebreak no terceiro set

### ITF (Regras Base)
- **Davis Cup**: Melhor de 5 sets (até quartas), melhor de 3 sets (finais)
- **Fed Cup/Billie Jean King Cup**: Melhor de 3 sets
- **Júnior**: Melhor de 3 sets

### Grand Slams - Regras Específicas

#### Australian Open
- Super tiebreak no quinto set (10 pontos)
- Teto retrátil ativa regra de calor extremo

#### Roland Garros
- Sem tiebreak no quinto set até 2022
- A partir de 2022: tiebreak em 6-6 no set decisivo

#### Wimbledon
- Tiebreak em 12-12 no set decisivo (desde 2019)
- Regra tradicional: sem tiebreak no set final

#### US Open
- Super tiebreak no quinto set (10 pontos)
- Primeira implementação do tiebreak (1970)

## ⚡ No-Ad Scoring

Sistema alternativo usado em alguns torneios:

### Regras
- Pontuação normal até 30-30
- Em 30-30 (Deuce): próximo ponto decide o game
- Jogador que recebe escolhe lado do saque
- Elimina jogos longos com múltiplos deuces

### Uso Atual
- **NextGen ATP Finals**: Todos os sets
- **Laver Cup**: Sets específicos
- **Alguns torneios juniores**: Para acelerar jogos

## 📊 Sistemas de Pontuação Especiais

### Fast4 Tennis
- Primeiro a 4 games (não 6)
- Tiebreak em 3-3
- No-ad scoring
- Let opcional (pode jogar)

### Match Tiebreak
- Substitui terceiro set completo
- Primeiro a 10 pontos (diferença de 2)
- Usado em duplas e alguns torneios mistos

### Set Curto
- Primeiro a 4 games com diferença de 2
- Se 4-4: tiebreak tradicional
- Usado em competições com tempo limitado

## 🔢 Exemplos Práticos

### Pontuação de Game Normal
```
0-0 → 15-0 → 15-15 → 30-15 → 30-30 → 40-30 → Game
```

### Pontuação com Deuce
```
0-0 → 15-15 → 30-30 → 40-40 (Deuce) → AD-40 → 40-40 (Deuce) → 40-AD → Game
```

### Tiebreak
```
6-6 → Tiebreak: 1-0 → 1-1 → 2-1 → 2-2 → 3-2 → 3-3 → 4-3 → 5-3 → 6-3 → 7-3
Set final: 7-6
```

## ⚖️ Regras de Implementação

### Validações do Sistema
1. **Pontuação válida**: Verificar se sequência de pontos é possível
2. **Duração mínima**: Games não podem ter menos de 4 pontos (exceto walkover)
3. **Alternância de saque**: Validar se sacador está correto
4. **Tiebreak**: Ativar automaticamente em 6-6

### Casos Especiais
- **Injury timeout**: Pontuação mantida, tempo não conta
- **Rain delay**: Pontuação mantida, pode afetar momentum
- **Code violation**: Penalty points afetam pontuação
- **Walkover**: Set 6-0, 6-0 ou 6-0, 6-0, 6-0

---

**Referências**: ITF Rules of Tennis 2024, ATP Official Rulebook 2024, WTA Official Rulebook 2024