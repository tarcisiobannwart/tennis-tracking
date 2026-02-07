# Deploy - Guia de Deployment

Este documento descreve o processo de deploy do Fina para produção.

## Arquitetura de Deploy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Fluxo de Deploy                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ git tag  │ →  │  GitHub  │ →  │   SSH    │ →  │ Servidor Prod    │  │
│  │ + push   │    │  Actions │    │  Deploy  │    │ (build local)    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────────┘  │
│                                                                          │
│  Local            CI/CD           Conexão         docker build + run     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Por que Git Pull + Build Local?

**Vantagens:**
- ✅ Sem custos de ECR/Registry
- ✅ Código fonte sempre disponível no servidor
- ✅ Builds otimizados para arquitetura do servidor
- ✅ Rollback simples via git checkout
- ✅ Debug mais fácil (código local)

**Trade-offs:**
- Build no servidor (poucos segundos para este projeto)
- Requer Docker instalado no servidor

---

## Processo de Deploy

### 1. Desenvolvimento Local

```bash
# Fazer alterações no código
# Testar localmente
make start
make test

# Commitar alterações
git add .
git commit -m "feat: nova funcionalidade"
```

### 2. Criar Tag de Release

```bash
# Criar e enviar tag (dispara deploy automático)
make deploy-tag TAG=v1.17.2

# Ou manualmente:
git tag v1.17.2
git push origin v1.17.2
```

### 3. GitHub Actions (Automático)

O workflow `.github/workflows/deploy.yml` é acionado automaticamente:

```yaml
on:
  push:
    tags:
      - 'v*'
```

**Etapas do workflow:**
1. Checkout do código
2. Conexão SSH com servidor
3. `git fetch --all --tags`
4. `git checkout <tag>`
5. `docker build -f Dockerfile.prod -t fina-app:<tag> .`
6. Stop container antigo
7. Start container novo
8. Health check

### 4. Verificar Deploy

```bash
# Via Makefile (requer SSH)
make deploy-status
make deploy-logs

# Ou diretamente no servidor
ssh usuario@servidor "docker ps | grep fina-app"
ssh usuario@servidor "docker logs fina-app --tail 50"
```

---

## Comandos do Makefile

### Deploy

| Comando | Descrição |
|---------|-----------|
| `make deploy-tag TAG=vX.Y.Z` | Criar tag e disparar deploy |
| `make deploy-local TAG=vX.Y.Z` | Build e deploy local (sem CI) |
| `make deploy-status` | Ver status do container em produção |
| `make deploy-logs` | Ver logs de produção |
| `make deploy-cleanup` | Limpar imagens antigas |

### Desenvolvimento

| Comando | Descrição |
|---------|-----------|
| `make start` | Iniciar ambiente local |
| `make stop` | Parar ambiente local |
| `make logs` | Ver logs locais |
| `make build TAG=vX.Y.Z` | Build local da imagem |

---

## Estrutura de Arquivos

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD workflow
├── Dockerfile.prod             # Dockerfile de produção
├── docker-compose.infra.yml    # Compose para infra compartilhada
├── Makefile                    # Comandos de automação
└── .env                        # Variáveis de ambiente
```

---

## GitHub Actions Workflow

### Arquivo: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

env:
  DEPLOY_PATH: /home/tarcisiobannwart/docker/fina
  CONTAINER_NAME: fina-app

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd ${{ env.DEPLOY_PATH }}

            # Pegar tag do GitHub ref
            TAG=${GITHUB_REF#refs/tags/}

            # Atualizar código
            git fetch --all --tags
            git checkout $TAG

            # Build da imagem
            docker build --platform linux/amd64 \
              -f Dockerfile.prod \
              -t fina-app:$TAG .

            # Parar container antigo
            docker stop fina-app 2>/dev/null || true
            docker rm fina-app 2>/dev/null || true

            # Iniciar novo container
            docker run -d \
              --name fina-app \
              --network docker_infra \
              --env-file .env \
              -p 12001:80 \
              --restart unless-stopped \
              fina-app:$TAG

            # Health check
            sleep 10
            curl -f http://localhost:12001/health || exit 1
```

### Secrets Necessários

Configure no GitHub Repository → Settings → Secrets:

| Secret | Descrição |
|--------|-----------|
| `SERVER_HOST` | IP ou hostname do servidor |
| `SERVER_USER` | Usuário SSH |
| `SERVER_SSH_KEY` | Chave privada SSH |

---

## Rollback

### Rollback Rápido (via tag anterior)

```bash
# No servidor
cd /home/tarcisiobannwart/docker/fina
git checkout v1.17.1
docker build -f Dockerfile.prod -t fina-app:v1.17.1 .
docker stop fina-app && docker rm fina-app
docker run -d --name fina-app --network docker_infra --env-file .env -p 12001:80 fina-app:v1.17.1
```

### Rollback via Imagem Existente

```bash
# Se a imagem ainda existir
docker stop fina-app && docker rm fina-app
docker run -d --name fina-app --network docker_infra --env-file .env -p 12001:80 fina-app:v1.17.1
```

---

## Infraestrutura Compartilhada

O Fina usa infraestrutura compartilhada via rede `docker_infra`:

| Serviço | Container | Porta Interna |
|---------|-----------|---------------|
| PostgreSQL | `infra-postgres` | 5432 |
| Redis | `infra-redis` | 6379 |
| MinIO | `minio` | 9000 |

### Verificar Conectividade

```bash
# No servidor
docker exec fina-app ping -c 1 infra-postgres
docker exec fina-app ping -c 1 infra-redis
docker exec fina-app ping -c 1 minio
```

---

## Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker logs fina-app

# Verificar se rede existe
docker network ls | grep docker_infra

# Verificar se infra está rodando
docker ps | grep -E "(postgres|redis|minio)"
```

### Erro de conexão com banco

```bash
# Verificar DATABASE_URL no .env
grep DATABASE_URL .env

# Testar conexão
docker exec fina-app python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Build falha

```bash
# Limpar cache do Docker
docker builder prune -f

# Build com logs detalhados
docker build --progress=plain -f Dockerfile.prod -t fina-app:test .
```

### Porta em uso

```bash
# Ver o que está usando a porta
sudo lsof -i :12001

# Parar container antigo
docker stop fina-app
docker rm fina-app
```

---

## Checklist de Deploy

- [ ] Código testado localmente
- [ ] Testes passando
- [ ] Commit feito e push para main/develop
- [ ] Tag criada com versionamento semântico (vX.Y.Z)
- [ ] Tag enviada para GitHub (`git push origin vX.Y.Z`)
- [ ] GitHub Actions executou com sucesso
- [ ] Container rodando em produção
- [ ] Health check passando
- [ ] Funcionalidade testada em produção

---

## Versionamento

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (v2.0.0): Mudanças incompatíveis
- **MINOR** (v1.18.0): Novas funcionalidades compatíveis
- **PATCH** (v1.17.2): Correções de bugs

```bash
# Ver versão atual
git describe --tags --abbrev=0

# Ver todas as tags
git tag -l "v*" | sort -V | tail -10
```

---

*Última atualização: 2026-02-05*
