# Comando: Deploy (Commit + Tag + GitHub Actions)

Executa o fluxo completo de deploy do Tennis Tracking: commit das alteracoes na branch main, criacao de tag de versao e push da tag que aciona o GitHub Actions workflow.

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
|    - Detectar ultima tag                                     |
|    - Calcular proxima versao (semver)                        |
|    - Gerar changelog                                         |
|    - Criar tag anotada                                       |
|    - Push tag (aciona GitHub Actions)                        |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
| 4. MONITORAR DEPLOY                                          |
|    - Exibir link do GitHub Actions                           |
|    - GitHub Actions faz: SSH + git pull + docker build       |
+-------------------------------------------------------------+
```

## Argumentos

`$ARGUMENTS`

| Argumento | Descricao | Exemplo |
|-----------|-----------|---------|
| (vazio) | Incrementa patch version (x.y.Z) | `v1.5.0` -> `v1.5.1` |
| `--minor` | Incrementa minor version (x.Y.0) | `v1.5.0` -> `v1.6.0` |
| `--major` | Incrementa major version (X.0.0) | `v1.5.0` -> `v2.0.0` |
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
git ls-remote --tags origin | grep -oP 'v\d+\.\d+\.\d+' | sort -V | tail -1

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
| `--major` | `MAJOR+1.0.0` | `1.5.0` -> `2.0.0` |
| `--minor` | `MAJOR.MINOR+1.0` | `1.5.0` -> `1.6.0` |
| (default/patch) | `MAJOR.MINOR.PATCH+1` | `1.5.0` -> `1.5.1` |

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
- Servidor: Producao (via GitHub Actions SSH)
- Compose: docker-compose.server.yml
- Health: http://localhost:5002/health

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

# Push tag (aciona o GitHub Actions automaticamente)
git push origin "v$NEW_VERSION"
```

### Passo 4: Monitorar Deploy

Apos o push da tag, o GitHub Actions workflow `deploy-on-tag.yml` eh acionado automaticamente.

**O workflow faz:**
1. Conecta via SSH ao servidor de producao
2. `git fetch --all --tags && git checkout v$NEW_VERSION`
3. `docker compose -f docker-compose.server.yml down`
4. `docker compose -f docker-compose.server.yml up -d --build`
5. Aguarda 30s e verifica health check em `http://localhost:5002/health`

**Link do GitHub Actions:**
```
https://github.com/tarcisiobannwart/tennis-tracking/actions
```

## Regras de Seguranca

### Verificacoes Obrigatorias

| Verificacao | Acao se Falhar |
|-------------|----------------|
| Branch atual eh `main` | Abortar |
| Nao ha alteracoes uncommitted | Sugerir commit primeiro |
| Main esta atualizado com remote | Abortar (pedir pull) |
| Tag nao existe | Abortar se ja existir |

### Protecoes

1. **NUNCA** fazer force push em main
2. **NUNCA** deletar tags existentes
3. **SEMPRE** criar tags anotadas (nao lightweight)
4. **SEMPRE** gerar changelog na tag
5. **SEMPRE** verificar que a tag nao existe antes de criar
6. **SEMPRE** usar formato semver vX.Y.Z para tags

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
   |- Ultima tag: v1.5.0
   |- Remote sync: OK

ETAPA 2: Commit
   |- Validacao Design System: OK
   |- Validacao Python: OK
   |- Commit: abc1234
   |- Push main: OK

ETAPA 3: Criar Tag
   |- Versao anterior: v1.5.0
   |- Tipo incremento: patch (auto-detectado)
   |- Nova versao: v1.5.1
   |- Changelog:
   |   - feat(frontend): adicionar filtros avancados
   |   - fix(backend): corrigir query de scoring
   |   - chore: atualizar dependencias
   |- Tag criada: OK
   |- Push tag: OK (GitHub Actions acionado)

ETAPA 4: Deploy
   |- GitHub Actions: https://github.com/tarcisiobannwart/tennis-tracking/actions
   |- O workflow ira:
   |   1. SSH no servidor de producao
   |   2. git checkout v1.5.1
   |   3. docker compose -f docker-compose.server.yml up -d --build
   |   4. Health check: http://localhost:5002/health

========================================================

DEPLOY INICIADO COM SUCESSO!

Resumo:
   - Versao: v1.5.1
   - Commits incluidos: 3

Proximos passos:
   - Monitorar workflow: https://github.com/tarcisiobannwart/tennis-tracking/actions
   - Verificar health: https://tennis.tarcisiobannwart.com/health
   - Frontend: https://tennis.tarcisiobannwart.com
```

### Dry Run

```
DEPLOY Tennis Tracking - Modo Dry Run (simulacao)
========================================================

O que seria executado:

1. COMMIT
   - 3 arquivos seriam commitados
   - Mensagem: "feat(frontend): adicionar filtros avancados"

2. TAG
   - Versao atual: v1.5.0
   - Nova versao: v1.5.1 (patch)
   - Commits incluidos: 3

3. DEPLOY
   - Tag v1.5.1 acionaria GitHub Actions workflow
   - SSH para servidor de producao
   - docker compose rebuild

========================================================

Nenhuma alteracao foi feita (dry run)
Execute sem --dry-run para aplicar
```

### Falha - Branch Incorreta

```
DEPLOY Tennis Tracking - Iniciando fluxo de release
========================================================

ETAPA 1: Verificacoes
   |- Branch atual: feature/new-feature
   |- ERRO: Branch deve ser 'main'

========================================================

DEPLOY ABORTADO - Branch incorreta

O Tennis Tracking faz deploy diretamente da branch main.
Faca merge da sua feature branch para main primeiro:

   git checkout main
   git merge feature/new-feature
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
git tag -a "v1.5.2" -m "Rollback: revert v1.5.1"
git push origin "v1.5.2"
```

### Rollback Manual (Emergencia)

```bash
# SSH no servidor de producao e voltar para tag anterior:
ssh user@<SERVER_IP>
cd /opt/tennis-tracking
git checkout v1.5.0
docker compose -f docker-compose.server.yml down
docker compose -f docker-compose.server.yml up -d --build
```

### Deploy Manual (sem GitHub Actions)

```bash
# Usar script de deploy direto:
./scripts/deploy_to_server.sh [username]
# Ou manualmente:
ssh user@192.168.0.21
cd /opt/tennis-tracking
git fetch --all --tags
git checkout v1.5.1
docker compose -f docker-compose.server.yml up -d --build
```

### Verificacao Pos-Deploy

```bash
# Health check da API (producao via dominio)
curl https://tennis.tarcisiobannwart.com/health

# Health check direto no servidor (IP interno)
curl http://192.168.0.21:5002/health
```

## Informacoes de Infraestrutura

| Item | Valor |
|------|-------|
| Servidor producao | `192.168.0.21` (via GitHub Secrets) |
| Diretorio no servidor | `/opt/tennis-tracking` |
| Porta da aplicacao | `5002` |
| Docker Compose | `docker-compose.server.yml` |
| Dockerfile | `Dockerfile` (multi-stage: frontend + backend + nginx) |
| Imagem unificada | `tennis-tracking-app` (nginx + fastapi + celery via supervisor) |
| Database | `infra-postgres:5432` (rede externa `docker_infra`) |
| Redis | `tennis-tracking-redis` (container local) |
| CI/CD | GitHub Actions (`deploy-on-tag.yml`) |
| GitHub Actions URL | `https://github.com/tarcisiobannwart/tennis-tracking/actions` |
| Branch de deploy | `main` |
| Formato de tag | `vX.Y.Z` (semver) |
| Frontend (prod) | `https://tennis.tarcisiobannwart.com` |
| API (prod) | `https://tennis.tarcisiobannwart.com/api` |
| CORS allowed | `https://tennis.tarcisiobannwart.com`, `http://localhost` |

## Comandos Relacionados

- `/commit` - Commit e push (etapa 1 do deploy)
- `/validate-design` - Validacao do frontend
- `/validate-backend` - Validacao do backend
- `/cves` - Analise de vulnerabilidades antes do deploy
