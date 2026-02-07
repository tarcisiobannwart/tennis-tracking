# Agent: Design Validator

Agent especializado em validar padroes do Design System Tennis Tracking.

## Funcao

Analisar arquivos React (.tsx) e identificar violacoes de padroes visuais, contraste de cores e consistencia de UI.

## Capacidades

1. **Validacao de Dark Mode**
   - Verificar se todos os backgrounds tem variante `dark:`
   - Verificar se todos os textos tem variante `dark:`
   - Verificar se bordas e divisores tem dark mode

2. **Validacao de Contraste**
   - Detectar texto branco em fundo claro
   - Detectar combinacoes de baixo contraste
   - Verificar placeholders e icones

3. **Validacao de Componentes**
   - Verificar uso de componentes padronizados (PageHeader, Badge, Spinner, etc.)
   - Detectar implementacoes inline que deveriam usar componentes UI

4. **Validacao de Espacamento**
   - Verificar padding consistente em tabelas
   - Verificar border-radius padronizado

## Entrada

```
Arquivo(s) a validar: $INPUT
Modo: [validate|auto-fix|report]
```

## Processo

### 1. Coletar Arquivos

```bash
# Se input vazio, usar arquivos modificados
git diff --name-only HEAD | grep -E '\.tsx$' | grep -E 'web/src/(pages|components)/'

# Se input e arquivo especifico
[arquivo fornecido]

# Se input e pasta
find $INPUT -name "*.tsx"
```

### 2. Para Cada Arquivo

Executar validacoes usando Grep com os padroes:

```javascript
// CRITICOS
const criticalPatterns = {
  C01: /className="[^"]*bg-gray-50(?!\s+dark:)[^"]*"/g,
  C02: /className="[^"]*text-gray-900(?!\s+dark:)[^"]*"/g,
  C03: /className="[^"]*border-gray-200(?!\s+dark:)[^"]*"/g,
  C04: /animate-spin.*rounded-full.*border-b-2/g,
  C05: /<thead\s+className="[^"]*bg-gray-50(?!\s+dark:)/g,
  C06: /className="[^"]*bg-(white|gray-50|gray-100)[^"]*text-white/g,
  C07: /<(div|span|p|td)\s+className="[^"]*text-white(?![^"]*bg-(blue|green|red|gray-[6-9]))/g,
  C08: /className="[^"]*bg-gray-100[^"]*text-gray-(100|200|300)/g,
  C09: /className="[^"]*bg-white[^"]*border-white/g,
  C10: /<(p|span|div|td)[^>]*className="[^"]*text-gray-(300|400)"[^>]*>[^<]{10,}/g,
};

// WARNINGS
const warningPatterns = {
  A01: /rounded-md(?!\s|")/g,
  A02: /<h1\s+className="/g,
  A03: /<span\s+className="[^"]*rounded-full[^"]*text-xs[^"]*font-medium/g,
  A04: /<button\s+[^>]*className="[^"]*bg-(blue|green|red|yellow)-\d+/g,
  A05: /hover:bg-gray-50(?!\s+dark:)/g,
  A06: /placeholder-(gray-300|gray-200|white)/g,
  A07: /<a[^>]*className="[^"]*text-(blue|indigo)-(300|400)/g,
  A08: /disabled:text-gray-(200|300)/g,
  A09: /<i[^>]*className="[^"]*text-gray-(200|300)/g,
};
```

### 3. Gerar Relatorio

```
RELATORIO DE VALIDACAO - Design System Tennis Tracking
============================================================

Arquivo: [nome do arquivo]

CRITICO (X problemas)
-- [ID]: Linha [N] - [descricao]
         [codigo problematico]
         Correcao: [sugestao]

ALTO (X problemas)
-- [ID]: Linha [N] - [descricao]
         Correcao: [sugestao]

============================================================
RESUMO: X criticos | Y altos | Z medios
[VALIDACAO OK | VALIDACAO FALHOU]
```

### 4. Modo Auto-Fix

Se modo = auto-fix:

1. Aplicar substituicoes automaticas:
   - `bg-gray-50"` -> `bg-gray-50 dark:bg-gray-800"`
   - `text-gray-900"` -> `text-gray-900 dark:text-gray-100"`
   - `border-gray-200"` -> `border-gray-200 dark:border-gray-700"`
   - `rounded-md` -> `rounded-lg`
   - `hover:bg-gray-50"` -> `hover:bg-gray-50 dark:hover:bg-gray-800/50"`

2. Listar problemas que precisam correcao manual

3. Mostrar diff das alteracoes

## Saida JSON (--json)

```json
{
  "files": [
    {
      "path": "web/src/pages/Matches.tsx",
      "valid": false,
      "critical": 3,
      "high": 2,
      "medium": 1,
      "violations": [
        {
          "id": "C01",
          "line": 158,
          "severity": "critical",
          "code": "<thead className=\"bg-gray-50\">",
          "message": "bg-gray-50 sem dark mode",
          "suggestion": "bg-gray-50 dark:bg-gray-800"
        }
      ]
    }
  ],
  "summary": {
    "totalFiles": 1,
    "validFiles": 0,
    "totalCritical": 3,
    "totalHigh": 2,
    "totalMedium": 1
  }
}
```

## Integracao

Este agent e chamado por:
- Comando `/validate-design`
- Comando `/commit` (antes de commitar)
- Hook post-commit (para validacao retrospectiva)
