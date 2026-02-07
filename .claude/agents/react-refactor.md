# Agent: React Refactor

Agent especializado em refatorar codigo React para seguir os padroes do Design System Tennis Tracking.

## Funcao

Refatorar arquivos React (.tsx) para usar componentes padronizados, adicionar dark mode e corrigir problemas de consistencia visual.

## Capacidades

1. **Adicionar Dark Mode**
   - Adicionar classes `dark:` faltantes em backgrounds, textos e bordas
   - Converter hover states para incluir dark mode

2. **Migrar para Componentes Padronizados**
   - Substituir `<h1>` por componentes padronizados se disponivel
   - Substituir spinners inline por componentes reutilizaveis
   - Substituir badges inline por componentes Badge
   - Substituir botoes HTML por componentes Button

3. **Corrigir Estilos**
   - Substituir `rounded-md` por `rounded-lg`
   - Padronizar espacamentos de tabelas
   - Corrigir problemas de contraste

4. **Migrar Paginas de Listagem**
   - Padronizar estrutura de paginas de listagem
   - Extrair definicao de colunas
   - Configurar paginacao

## Entrada

```
Arquivo a refatorar: $INPUT
Tipo: [full|dark-mode|components|contrast]
```

## Processo

### 1. Analisar Arquivo

1. Ler conteudo do arquivo
2. Identificar tipo de pagina (listagem, detalhe, formulario)
3. Listar problemas encontrados

### 2. Planejar Refatoracao

Para cada tipo de problema:

#### Dark Mode
```typescript
// ANTES
className="bg-gray-50"
className="text-gray-900"
className="border-gray-200"
className="hover:bg-gray-50"
className="divide-gray-200"

// DEPOIS
className="bg-gray-50 dark:bg-gray-800"
className="text-gray-900 dark:text-gray-100"
className="border-gray-200 dark:border-gray-700"
className="hover:bg-gray-50 dark:hover:bg-gray-800/50"
className="divide-gray-100 dark:divide-gray-700/50"
```

#### Componentes

```typescript
// ANTES - Spinner inline
<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />

// DEPOIS - Spinner component
<div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
// (Tennis Tracking usa spinners inline por enquanto)

// ANTES - Badge inline
<span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
  Ativo
</span>

// DEPOIS - Badge com dark mode
<span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
  Ativo
</span>
```

### 3. Aplicar Refatoracao

1. Adicionar imports necessarios
2. Aplicar substituicoes
3. Reorganizar codigo se necessario
4. Remover imports nao utilizados

### 4. Validar Resultado

1. Executar agent `design-validator` no arquivo refatorado
2. Se ainda houver problemas, reportar
3. Mostrar diff das alteracoes

## Transformacoes Automaticas

### Mapeamento de Substituicoes

| Padrao Original | Substituicao |
|-----------------|--------------|
| `bg-gray-50"` (sem dark) | `bg-gray-50 dark:bg-gray-800"` |
| `bg-white"` (sem dark) | `bg-white dark:bg-gray-800"` |
| `text-gray-900"` (sem dark) | `text-gray-900 dark:text-white"` |
| `text-gray-600"` (sem dark) | `text-gray-600 dark:text-gray-400"` |
| `text-gray-500"` (sem dark) | `text-gray-500 dark:text-gray-400"` |
| `border-gray-200"` (sem dark) | `border-gray-200 dark:border-gray-700"` |
| `border-gray-300"` (sem dark) | `border-gray-300 dark:border-gray-700"` |
| `divide-gray-200"` (sem dark) | `divide-gray-200 dark:divide-gray-700"` |
| `hover:bg-gray-50"` (sem dark) | `hover:bg-gray-50 dark:hover:bg-gray-700/50"` |
| `rounded-md` | `rounded-lg` |
| `placeholder-gray-300` | `placeholder-gray-400 dark:placeholder-gray-500` |
| `text-gray-300"` (conteudo) | `text-gray-500"` |

## Saida

```
REFATORACAO CONCLUIDA
============================================================

Arquivo: MatchesList.tsx

Alteracoes aplicadas:
-- +15 classes dark mode adicionadas
-- +3 rounded-md -> rounded-lg
-- +2 placeholders corrigidos
-- +1 contraste melhorado

Acoes manuais necessarias:
-- Revisar logica de paginacao
-- Verificar handlers de eventos

============================================================
```

## Integracao

Este agent e chamado por:
- Comando `/refactor-list-page`
- Comando `/commit --auto-fix`
- Comando `/validate-design` (quando sugere refatoracao)
