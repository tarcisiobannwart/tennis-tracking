# Comando: Criar/Atualizar Traducoes

Crie ou atualize traducoes i18n para o Tennis Tracking.

## Agents Utilizados

- **Principal**: `~/.claude/agents/agent-react.md`

## Idiomas Suportados

- pt-BR (Portugues Brasil) - Principal
- en-US (English)

## Estrutura de Arquivos

```
web/src/i18n/
├── pt-BR/
│   ├── common.json
│   ├── dashboard.json
│   ├── analysis.json
│   ├── matches.json
│   └── players.json
└── en-US/
    ├── common.json
    ├── dashboard.json
    ├── analysis.json
    ├── matches.json
    └── players.json
```

## Instrucoes

Entrada do usuario: `$ARGUMENTS`

1. **Chaves especificas**: Adicione em TODOS os idiomas
2. **Sincronizar**: Compare pt-BR com en-US e adicione faltantes
3. **Formato**: dot notation (`actions.save`, `messages.success`)

## Regras

- pt-BR e a lingua de referencia
- Mesma estrutura em todos os idiomas
- Traducoes naturais, nao literais
- Preservar placeholders `{name}`, `{count}`

## Vocabulario de Tenis

| pt-BR | en-US |
|-------|-------|
| Partida | Match |
| Jogo | Game |
| Set | Set |
| Ponto | Point |
| Saque | Serve |
| Devolucao | Return |
| Voleio | Volley |
| Quique | Bounce |
| Quadra | Court |
| Linha de Base | Baseline |
| Rede | Net |
| Jogador | Player |
| Placar | Score |
| Ace | Ace |
| Dupla Falta | Double Fault |
| Break Point | Break Point |
| Tiebreak | Tiebreak |
| Forehand | Forehand |
| Backhand | Backhand |
| Smash | Smash |
| Lob | Lob |
| Drop Shot | Drop Shot |
