# Comando: Validar Design System

Valida se uma pagina React segue os padroes do Design System Tennis Tracking.

## Integracao com Jira

Quando problemas sao encontrados:
1. Perguntar se deseja criar issue no Jira (rastreabilidade)
2. Se sim, criar issue via `/create-jira`
3. Executar correcao automatica
4. Commit vinculado a issue
5. Issue movida para Done automaticamente

## Instrucoes

Arquivo/pasta a validar: `$ARGUMENTS`
- Se vazio: valida arquivos modificados (git diff)
- Se informado: valida arquivo ou pasta especifica

## Regras de Validacao

### CRITICO (bloqueia commit)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| C01 | Dark mode em backgrounds | `bg-gray-50"` (sem dark:) | `bg-gray-50 dark:bg-gray-800"` |
| C02 | Dark mode em textos | `text-gray-900"` (sem dark:) | `text-gray-900 dark:text-gray-100"` |
| C03 | Dark mode em bordas | `border-gray-200"` (sem dark:) | `border-gray-200 dark:border-gray-700"` |
| C04 | Spinner inline | `animate-spin.*border-b-2` | `<Spinner />` |
| C05 | Tabela inline sem dark | `<thead className="bg-gray-50">` | `<TableHead>` ou com dark: |

### ALTO (warning, deve corrigir)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| A01 | Border-radius inconsistente | `rounded-md` | `rounded-lg` |
| A02 | H1 inline | `<h1 className=` | `<PageHeader title=` |
| A03 | Badge inline | `<span.*rounded-full.*text-xs` | `<Badge>` |
| A04 | Botao HTML | `<button className=".*bg-blue` | `<Button variant=` |
| A05 | Hover sem dark | `hover:bg-gray-50"` | `hover:bg-gray-50 dark:hover:bg-gray-800` |

### CRITICO - Contraste de Cores (ilegibilidade)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| C06 | Texto branco em fundo claro | `bg-white.*text-white` ou `bg-gray-50.*text-white` | Usar texto escuro ou fundo escuro |
| C07 | Texto claro sem dark variant | `text-white"` (sem condicao) em area de conteudo | `text-white` so em fundos escuros garantidos |
| C08 | Botao sem contraste | `bg-white.*text-gray-100` ou `bg-gray-100.*text-gray-200` | Minimo 4.5:1 de contraste |
| C09 | Botao outline invisivel | `border-white` em fundo branco | Usar border com contraste |
| C10 | Texto gray-300/400 em fundo claro | `text-gray-300"` ou `text-gray-400"` em conteudo principal | `text-gray-500` minimo para legibilidade |

### ALTO - Problemas de Contraste

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| A06 | Placeholder muito claro | `placeholder-gray-300` | `placeholder-gray-400` minimo |
| A07 | Link sem destaque | `text-blue-300` em fundo claro | `text-blue-600` para links |
| A08 | Disabled muito claro | `disabled:text-gray-200` | `disabled:text-gray-400` |
| A09 | Icon sem contraste | `text-gray-200` para icones | `text-gray-400` minimo |

### MEDIO (sugestao)

| ID | Regra | Padrao Incorreto | Padrao Correto |
|----|-------|------------------|----------------|
| M01 | Espacamento tabela | `px-6 py-4` | `px-4 py-3` |
| M02 | Divisor sem dark | `divide-gray-200` | `divide-gray-100 dark:divide-gray-700` |
| M03 | Pagina sem ListPageLayout | paginas de listagem sem wrapper | `<ListPageLayout>` |
| M04 | Borda muito clara | `border-gray-100` | `border-gray-200` minimo |

## Processo de Validacao

### Passo 1: Identificar Arquivos

```bash
# Se $ARGUMENTS vazio, pegar arquivos modificados
git diff --name-only --diff-filter=AM | grep -E '\.(tsx|jsx)$' | grep -E '^frontend/src/(pages|components)/'
```

### Passo 2: Analisar Cada Arquivo

Para cada arquivo .tsx de pagina:

1. **Ler o conteudo do arquivo**
2. **Executar validacoes com Grep/regex**
3. **Coletar violacoes**

### Passo 3: Gerar Relatorio

```
RELATORIO DE VALIDACAO - Design System Tennis Tracking
========================================================

Arquivo: frontend/src/pages/Clients.tsx

CRITICO (3 problemas)
|- C01: Linha 158 - bg-gray-50 sem dark mode
|       <thead className="bg-gray-50">
|       Correcao: bg-gray-50 dark:bg-gray-800
|
|- C02: Linha 192 - text-gray-900 sem dark mode
|       <td className="px-4 py-3 text-gray-900">
|       Correcao: text-gray-900 dark:text-gray-100
|
|- C04: Linha 174 - Spinner inline
        <div className="animate-spin rounded-full h-8 w-8 border-b-2">
        Correcao: usar <Spinner size="lg" />

ALTO (2 problemas)
|- A01: Linha 280 - rounded-md inconsistente
|       <input className="rounded-md border">
|       Correcao: usar rounded-lg
|
|- A02: Linha 84 - H1 inline
        <h1 className="text-2xl font-bold">
        Correcao: usar <PageHeader title="..." />

========================================================
RESUMO: 3 criticos | 2 altos | 0 medios
VALIDACAO FALHOU - Correcoes necessarias
```

### Passo 4: Decisao Automatica

Se houver problemas **CRITICOS**:
1. Perguntar: "Deseja executar refatoracao automatica? (S/N)"
2. Se SIM: aplicar correcoes automaticas
3. Se NAO: listar correcoes manuais necessarias

## Padroes de Busca (Regex)

```javascript
// C01: Background sem dark mode
/className="[^"]*bg-gray-50(?!\s+dark:)[^"]*"/g

// C02: Texto sem dark mode
/className="[^"]*text-gray-900(?!\s+dark:)[^"]*"/g

// C03: Borda sem dark mode
/className="[^"]*border-gray-200(?!\s+dark:)[^"]*"/g

// C04: Spinner inline
/animate-spin.*rounded-full.*border-b-2/g

// C05: Thead sem dark mode
/<thead\s+className="[^"]*bg-gray-50(?!\s+dark:)[^"]*">/g

// A01: Border-radius inconsistente
/rounded-md(?!\s|")/g

// A02: H1 inline (em paginas)
/<h1\s+className="/g

// A03: Badge inline
/<span\s+className="[^"]*rounded-full[^"]*text-xs[^"]*font-medium/g

// A04: Botao HTML com estilo
/<button\s+[^>]*className="[^"]*bg-(blue|green|red|yellow)-\d+/g

// A05: Hover sem dark mode
/hover:bg-gray-50(?!\s+dark:)/g

// ========== CONTRASTE DE CORES ==========

// C06: Texto branco em fundo claro (potencial invisibilidade)
/className="[^"]*bg-(white|gray-50|gray-100)[^"]*text-white[^"]*"/g
/className="[^"]*text-white[^"]*bg-(white|gray-50|gray-100)[^"]*"/g

// C07: Texto branco solto (sem estar em botao/badge com fundo garantido)
/<(div|span|p|td|th)\s+className="[^"]*text-white(?![^"]*bg-(blue|green|red|yellow|indigo|purple|pink|gray-[6-9]00|black))[^"]*"/g

// C08: Combinacoes de baixo contraste
/className="[^"]*bg-gray-100[^"]*text-gray-(100|200|300)[^"]*"/g
/className="[^"]*bg-white[^"]*text-gray-(100|200|300)[^"]*"/g

// C09: Borda invisivel em fundo branco
/className="[^"]*bg-white[^"]*border-white[^"]*"/g
/className="[^"]*border-white[^"]*bg-white[^"]*"/g

// C10: Texto muito claro para conteudo principal
/<(p|span|div|td)[^>]*className="[^"]*text-gray-(300|400)"[^>]*>[^<]{10,}/g

// A06: Placeholder muito claro
/placeholder-(gray-300|gray-200|white)/g

// A07: Link com cor muito clara
/<a[^>]*className="[^"]*text-(blue|indigo)-(300|400)[^"]*"/g

// A08: Disabled muito claro
/disabled:text-gray-(200|300)/g

// A09: Icone sem contraste
/<i[^>]*className="[^"]*text-gray-(200|300)[^"]*"/g
```

## Integracao com /commit

Quando chamado pelo comando `/commit`:
1. Validar arquivos .tsx modificados
2. Se CRITICOS > 0: bloquear commit, sugerir refatoracao
3. Se apenas ALTOS: warning, permitir commit com confirmacao
4. Se apenas MEDIOS: informativo, permitir commit

## Modo Automatico (--auto-fix)

Se chamado com `--auto-fix`:
1. Aplicar correcoes automaticas para problemas simples:
   - Adicionar `dark:` classes faltantes
   - Trocar `rounded-md` por `rounded-lg`
2. Listar correcoes que precisam de intervencao manual
3. Mostrar diff das alteracoes

## Saida JSON (--json)

Para integracao com CI/CD:
```json
{
  "file": "Clients.tsx",
  "valid": false,
  "critical": 3,
  "high": 2,
  "medium": 0,
  "violations": [
    {
      "id": "C01",
      "line": 158,
      "severity": "critical",
      "message": "bg-gray-50 sem dark mode",
      "suggestion": "bg-gray-50 dark:bg-gray-800"
    }
  ]
}
```

## Mapeamento de Epics

| Pagina Frontend | Epic Jira |
|-----------------|-----------|
| Clients.tsx, ClientDetail.tsx | TT-11 (Clientes) |
| HR.tsx | TT-12 (RH) |
| FinanceCosts.tsx, Accounting.tsx, FinanceConciliation.tsx | TT-13 (Financeiro) |
| Opportunities.tsx, OpportunityDetail.tsx | TT-14 (CRM) |
| ServerOperations.tsx, DataMigrations.tsx | TT-15 (Infraestrutura) |
| Users.tsx, Security.tsx, MenuAccess.tsx | TT-16 (Configuracoes) |

## Exemplo de Uso

```bash
/validate-design                              # Valida arquivos modificados
/validate-design frontend/src/pages/Clients.tsx  # Valida arquivo especifico
/validate-design frontend/src/pages/           # Valida pasta
/validate-design --auto-fix                    # Corrige automaticamente
/validate-design --json                        # Saida JSON
```
