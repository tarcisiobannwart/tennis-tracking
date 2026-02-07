# Comando: Deploy (Commit + Tag + Pipeline)

Executa o fluxo completo de deploy do Tennis Tracking: commit das alteracoes na branch main, criacao de tag de versao e push da tag que aciona o Bitbucket Pipeline.

> **NOTA**: Referencias a Bitbucket Pipelines, AWS ECR e URLs devem ser atualizadas conforme o CI/CD do Tennis Tracking. O fluxo geral (commit → tag → pipeline) permanece valido.

## Fluxo de Execucao

```
+-------------------------------------------------------------+
|                       /deploy                                 |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
| 1. VERIFICACOES                                              |
|    - Branch atual eh main?                                   |
|    - Ha alteracoes pendentes?                                |
|    - Main esta sincronizada com remote?                      |
|    - Ultima tag existente?                                   |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
| 2. COMMIT (executa /commit se houver alteracoes)             |
|    - Valida Design System (React)                            |
|    - Valida Padroes Python                                   |
|    - Cria commit semantico                                   |
|    - Push para main                                          |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
| 3. CRIAR TAG                                                 |
|    - Detectar ultima tag (v1.0.XX)                           |
|    - Calcular proxima versao (semver)                        |
|    - Gerar changelog                                         |
|    - Criar tag anotada                                       |
|    - Push tag (aciona Bitbucket Pipeline)                    |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
| 4. MONITORAR PIPELINE                                        |
|    - Exibir link do pipeline                                 |
|    - Pipeline faz: build AMD64 + push ECR + update server    |
+-------------------------------------------------------------+
```

## Argumentos

`$ARGUMENTS`

| Argumento | Descricao | Exemplo |
|-----------|-----------|---------|
| (vazio) | Incrementa patch version (x.y.Z) | `v1.0.3` -> `v1.0.4` |
| `--minor` | Incrementa minor version (x.Y.0) | `v1.0.3` -> `v1.1.0` |
| `--major` | Incrementa major version (X.0.0) | `v1.0.3` -> `v2.0.0` |
| `--version=X.Y.Z` | Define versao especifica | `--version=2.0.0` |
| `--skip-commit` | Pula etapa de commit (ja commitado) | |
| `--dry-run` | Mostra o que seria feito sem executar | |

## Instrucoes

### Passo 1: Verificar Estado Atual

```bash
# Verificar branch atual (deve ser main)
git branch --show-current

# Verificar se ha alteracoes pendentes
git status --porcelain

# Verificar ultima tag
git describe --tags --abbrev=0 2>/dev/null || echo "Nenhuma tag encontrada"

# Verificar tags remotas (para pegar a mais recente)
git ls-remote --tags origin | grep -oP 'v1\.\d+\.\d+' | sort -V | tail -1

# Verificar se main esta atualizado com remote
git fetch origin
git status -uno
```

### Passo 2: Commit (se houver alteracoes)

Se houver alteracoes pendentes e `--skip-commit` nao foi passado:

1. Executar validacoes do /commit
2. Criar commit semantico
3. Push para main

```bash
# Ja coberto pelo /commit
git push origin main
```

### Passo 3: Criar Tag

#### Detectar Ultima Versao

```bash
# Obter ultima tag local
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v1.0.0")
echo "Ultima tag: $LAST_TAG"

# Ou obter ultima tag remota (mais confiavel)
LAST_TAG=$(git ls-remote --tags origin | grep -oP 'v\d+\.\d+\.\d+' | sort -V | tail -1)

# Extrair componentes da versao
VERSION=${LAST_TAG#v}
MAJOR=$(echo $VERSION | cut -d. -f1)
MINOR=$(echo $VERSION | cut -d. -f2)
PATCH=$(echo $VERSION | cut -d. -f3)
```

#### Calcular Proxima Versao

| Tipo de Incremento | Formula | Exemplo |
|--------------------|---------|---------|
| `--major` | `MAJOR+1.0.0` | `1.0.3` -> `2.0.0` |
| `--minor` | `MAJOR.MINOR+1.0` | `1.0.3` -> `1.1.0` |
| (default/patch) | `MAJOR.MINOR.PATCH+1` | `1.0.3` -> `1.0.4` |

#### Deteccao Automatica de Versao

```bash
# Analisar commits desde ultima tag
COMMITS=$(git log $LAST_TAG..HEAD --pretty=format:"%s")

# Verificar tipo de incremento necessario
if echo "$COMMITS" | grep -qE "^(feat|fix|refactor)(\(.+\))?!:|BREAKING CHANGE"; then
    INCREMENT="major"
elif echo "$COMMITS" | grep -qE "^feat(\(.+\))?:"; then
    INCREMENT="minor"
else
    INCREMENT="patch"
fi

echo "Incremento sugerido: $INCREMENT"
```

#### Gerar Changelog

```bash
# Gerar changelog desde ultima tag
CHANGELOG=$(git log $LAST_TAG..HEAD --pretty=format:"- %s" --no-merges)
```

#### Criar Tag Anotada

```bash
# Criar tag anotada
git tag -a "v$NEW_VERSION" -m "$(cat <<EOF
Release v$NEW_VERSION

## Changelog

$CHANGELOG

## Informacoes
- Data: $(date +%Y-%m-%d)
- Branch: main
- Commit: $(git rev-parse HEAD)

## Deploy
- Registry: 021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub
- Plataforma: linux/amd64
- Pipeline: Bitbucket Pipelines (triggered by tag)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Push tag (aciona o Bitbucket Pipeline automaticamente)
git push origin "v$NEW_VERSION"
```

### Passo 4: Monitorar Pipeline

Apos o push da tag, o Bitbucket Pipeline eh acionado automaticamente.

**O pipeline faz:**
1. Build da imagem Docker com `--platform linux/amd64 -f Dockerfile.unified`
2. Push para ECR: `021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub:v$NEW_VERSION`
3. Push para ECR: `021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub:latest`
4. Atualiza o container no servidor de producao

**Link do pipeline:**
```
https://bitbucket.org/phdesignsystems/tennis-tracking/pipelines
```

## Regras de Seguranca

### Verificacoes Obrigatorias

| Verificacao | Acao se Falhar |
|-------------|----------------|
| Branch atual eh `main` | Abortar (TMF usa main diretamente) |
| Nao ha alteracoes uncommitted | Sugerir commit primeiro |
| Main esta atualizado com remote | Abortar (pedir pull) |
| Tag nao existe | Abortar se ja existir |

### Protecoes

1. **NUNCA** fazer force push em main
2. **NUNCA** deletar tags existentes
3. **SEMPRE** criar tags anotadas (nao lightweight)
4. **SEMPRE** gerar changelog na tag
5. **SEMPRE** verificar que a tag nao existe antes de criar
6. **SEMPRE** usar formato v1.0.XX para tags

## Fluxo de Decisao para Versao

```
+-------------------------------------------------------------+
| Analisar commits desde ultima tag                            |
+----------------------------+--------------------------------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
    feat! ou            feat:            fix:, refactor:,
    BREAKING CHANGE                      chore:, docs:
         |                   |                   |
         v                   v                   v
    +---------+         +---------+         +---------+
    | MAJOR   |         | MINOR   |         | PATCH   |
    | X.0.0   |         | x.Y.0   |         | x.y.Z   |
    +---------+         +---------+         +---------+
```

## Exemplo de Saida

### Sucesso

```
DEPLOY Tennis Tracking - Iniciando fluxo de release
========================================================

ETAPA 1: Verificacoes
   |- Branch atual: main
   |- Alteracoes pendentes: 3 arquivos
   |- Ultima tag: v1.0.12
   |- Remote sync: OK

ETAPA 2: Commit
   |- Validacao Design System: OK
   |- Validacao Python: OK
   |- Commit: abc1234
   |- Push main: OK

ETAPA 3: Criar Tag
   |- Versao anterior: v1.0.12
   |- Tipo incremento: patch (auto-detectado)
   |- Nova versao: v1.0.13
   |- Changelog:
   |   - feat(clients): adicionar filtros avancados
   |   - fix(hr): corrigir calculo de folha
   |   - chore: atualizar dependencias
   |- Tag criada: OK
   |- Push tag: OK (pipeline acionado)

ETAPA 4: Pipeline
   |- URL: https://bitbucket.org/phdesignsystems/tennis-tracking/pipelines
   |- O pipeline ira:
   |   1. Build imagem: docker build --platform linux/amd64 -f Dockerfile.unified
   |   2. Push ECR: tmf-hub:v1.0.13 + tmf-hub:latest
   |   3. Atualizar container em producao

========================================================

DEPLOY INICIADO COM SUCESSO!

Resumo:
   - Versao: v1.0.13
   - Commits incluidos: 3
   - ECR: 021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub:v1.0.13

Proximos passos:
   - Monitorar pipeline: https://bitbucket.org/phdesignsystems/tennis-tracking/pipelines
   - Verificar health: https://hub-api.trademarketingforce.com/health
   - Frontend: https://hub.trademarketingforce.com
```

### Dry Run

```
DEPLOY Tennis Tracking - Modo Dry Run (simulacao)
========================================================

O que seria executado:

1. COMMIT
   - 3 arquivos seriam commitados
   - Mensagem: "feat(clients): adicionar filtros avancados"

2. TAG
   - Versao atual: v1.0.12
   - Nova versao: v1.0.13 (patch)
   - Commits incluidos: 3

3. PIPELINE
   - Tag v1.0.13 acionaria o Bitbucket Pipeline
   - Imagem: tmf-hub:v1.0.13
   - Registry: 021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub

========================================================

Nenhuma alteracao foi feita (dry run)
Execute sem --dry-run para aplicar
```

### Falha - Branch Incorreta

```
DEPLOY Tennis Tracking - Iniciando fluxo de release
========================================================

ETAPA 1: Verificacoes
   |- Branch atual: feature/clients-filters
   |- ERRO: Branch deve ser 'main'

========================================================

DEPLOY ABORTADO - Branch incorreta

O Tennis Tracking faz deploy diretamente da branch main.
Faca merge da sua feature branch para main primeiro:

   git checkout main
   git merge feature/clients-filters
   git push origin main

Depois execute /deploy novamente.
```

## Rollback

Se algo der errado apos o deploy:

### Rollback via Nova Tag

```bash
# Opcao 1: Revert do ultimo commit e nova tag
git checkout main
git revert HEAD --no-edit
git push origin main

# Criar nova tag patch com o revert
git tag -a "v1.0.14" -m "Rollback: revert v1.0.13"
git push origin "v1.0.14"
```

### Rollback Manual (Emergencia)

```bash
# No servidor de producao, voltar para tag anterior
# SSH no servidor e executar:
docker pull 021301014509.dkr.ecr.us-east-1.amazonaws.com/tmf-hub:v1.0.12
docker compose up -d
```

### Verificacao Pos-Deploy

```bash
# Health check da API
curl https://hub-api.trademarketingforce.com/health

# Health check do banco
curl https://hub-api.trademarketingforce.com/health/db

# Health check do Redis
curl https://hub-api.trademarketingforce.com/health/redis
```

## Informacoes de Infraestrutura

| Item | Valor |
|------|-------|
| ECR Registry | `021301014509.dkr.ecr.us-east-1.amazonaws.com` |
| ECR Repository | `tmf-hub` |
| Regiao AWS | `us-east-1` |
| Plataforma | `linux/amd64` |
| Dockerfile | `Dockerfile.unified` |
| Branch de deploy | `main` |
| Formato de tag | `v1.0.XX` |
| Pipeline | Bitbucket Pipelines |
| Pipeline URL | `https://bitbucket.org/phdesignsystems/tennis-tracking/pipelines` |
| Frontend (prod) | `https://hub.trademarketingforce.com` |
| API (prod) | `https://hub-api.trademarketingforce.com` |

## Comandos Relacionados

- `/commit` - Commit e push (etapa 1 do deploy)
- `/validate-design` - Validacao do frontend
- `/validate-backend` - Validacao do backend
- `/cves` - Analise de vulnerabilidades antes do deploy
