# MinIO - Guia de Configuração para Aplicações

Este documento descreve como configurar o MinIO para aplicações usando a infraestrutura compartilhada.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         MinIO Server                            │
│                     (infra compartilhada)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   fina   │  │ tmf-hub  │  │   dani   │  │  app-x   │       │
│  │ (bucket) │  │ (bucket) │  │ (bucket) │  │ (bucket) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │              │             │             │              │
│  ┌────┴────┐    ┌────┴────┐  ┌────┴────┐  ┌────┴────┐        │
│  │fina-app │    │dev-team │  │dani-app │  │ app-x   │        │
│  │(usuário)│    │(usuário)│  │(usuário)│  │(usuário)│        │
│  └─────────┘    └─────────┘  └─────────┘  └─────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    tarcisio (superadmin)                 │  │
│  │                    Acesso total a todos buckets          │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Estrutura de Usuários

| Tipo | Exemplo | Acesso | Uso |
|------|---------|--------|-----|
| **Superadmin** | `tarcisio` | Todos buckets | Administração geral |
| **App User** | `fina-app` | Só seu bucket | Aplicação em produção |
| **Dev Team** | `dev-team` | Buckets específicos | Desenvolvimento |

## Padrão: 1 Bucket por Aplicação

Cada aplicação tem **um único bucket** com **pastas internas**:

```
app-name/
├── documents/      # Documentos gerais
├── uploads/        # Uploads de usuários
├── exports/        # Relatórios exportados
├── receipts/       # Recibos/comprovantes
├── backups/        # Backups internos
└── temp/           # Arquivos temporários
```

**Por que um bucket único?**
- Simplifica gerenciamento de permissões
- Facilita backup (um comando)
- Policies por pasta quando necessário

---

## Passo a Passo: Adicionar Nova Aplicação

### 1. Criar Bucket

```bash
docker exec minio mc mb local/NOME-APP
```

### 2. Criar Policy da Aplicação

```bash
docker exec minio sh -c 'cat > /tmp/policy-NOME-APP.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::NOME-APP",
        "arn:aws:s3:::NOME-APP/*"
      ]
    }
  ]
}
EOF'

docker exec minio mc admin policy create local NOME-APP /tmp/policy-NOME-APP.json
```

### 3. Criar Usuário da Aplicação

```bash
# Gerar senha segura
SENHA=$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)

# Criar usuário
docker exec minio mc admin user add local NOME-APP-user "$SENHA"

# Atribuir policy
docker exec minio mc admin policy attach local NOME-APP --user NOME-APP-user

# IMPORTANTE: Salvar credenciais
echo "Access Key: NOME-APP-user"
echo "Secret Key: $SENHA"
```

### 4. Configurar Aplicação (.env)

```env
# MinIO Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=NOME-APP-user
MINIO_SECRET_KEY=SENHA_GERADA
MINIO_BUCKET=NOME-APP
MINIO_SECURE=false
```

### 5. Configurar Docker Compose

```yaml
services:
  app:
    environment:
      - MINIO_ENDPOINT=${MINIO_ENDPOINT:-minio:9000}
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - MINIO_BUCKET=${MINIO_BUCKET:-NOME-APP}
      - MINIO_SECURE=${MINIO_SECURE:-false}
    networks:
      - docker_infra

networks:
  docker_infra:
    external: true
```

---

## Políticas Avançadas

### Acesso Somente Leitura

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::NOME-APP",
        "arn:aws:s3:::NOME-APP/*"
      ]
    }
  ]
}
```

### Acesso a Pasta Específica

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::NOME-APP/exports/*"
      ]
    }
  ]
}
```

### Acesso a Múltiplos Buckets

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": [
        "arn:aws:s3:::bucket1",
        "arn:aws:s3:::bucket1/*",
        "arn:aws:s3:::bucket2",
        "arn:aws:s3:::bucket2/*"
      ]
    }
  ]
}
```

---

## Comandos Úteis

### Gerenciamento de Buckets

```bash
# Listar buckets
docker exec minio mc ls local/

# Criar bucket
docker exec minio mc mb local/NOME

# Remover bucket (vazio)
docker exec minio mc rb local/NOME

# Remover bucket (com conteúdo)
docker exec minio mc rb --force local/NOME

# Ver tamanho do bucket
docker exec minio mc du local/NOME
```

### Gerenciamento de Usuários

```bash
# Listar usuários
docker exec minio mc admin user list local/

# Criar usuário
docker exec minio mc admin user add local USUARIO SENHA

# Remover usuário
docker exec minio mc admin user remove local USUARIO

# Desabilitar usuário
docker exec minio mc admin user disable local USUARIO

# Habilitar usuário
docker exec minio mc admin user enable local USUARIO
```

### Gerenciamento de Policies

```bash
# Listar policies
docker exec minio mc admin policy list local/

# Ver detalhes de policy
docker exec minio mc admin policy info local NOME-POLICY

# Criar policy
docker exec minio mc admin policy create local NOME /tmp/policy.json

# Remover policy
docker exec minio mc admin policy remove local NOME

# Atribuir policy a usuário
docker exec minio mc admin policy attach local NOME-POLICY --user USUARIO
```

### Verificar Acesso

```bash
# Criar alias com credenciais do usuário
docker exec minio mc alias set teste http://localhost:9000 USUARIO SENHA

# Testar listagem
docker exec minio mc ls teste/BUCKET/

# Testar upload
echo "test" | docker exec -i minio mc pipe teste/BUCKET/test.txt

# Testar download
docker exec minio mc cat teste/BUCKET/test.txt

# Remover alias de teste
docker exec minio mc alias rm teste
```

---

## Backup

### Script de Backup por Aplicação

```bash
#!/bin/bash
APP_NAME="fina"
BACKUP_DIR="/home/tarcisiobannwart/docker/backups/$APP_NAME"
DATE=$(date +%Y%m%d_%H%M%S)

# Credenciais do usuário da aplicação
MINIO_ACCESS_KEY="fina-app"
MINIO_SECRET_KEY="z09DwR6NDzfBvmhky3ZKbw"

mkdir -p "$BACKUP_DIR"

# Configurar alias
docker exec minio mc alias set backup http://localhost:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

# Fazer backup
docker exec minio mc mirror backup/$APP_NAME /tmp/$APP_NAME
docker exec minio tar czf /tmp/${APP_NAME}_$DATE.tar.gz -C /tmp $APP_NAME
docker cp minio:/tmp/${APP_NAME}_$DATE.tar.gz "$BACKUP_DIR/"
docker exec minio rm -rf /tmp/$APP_NAME /tmp/${APP_NAME}_$DATE.tar.gz

echo "Backup salvo: $BACKUP_DIR/${APP_NAME}_$DATE.tar.gz"
```

---

## Acesso via Console Web

- **URL**: http://localhost:9001
- **Usuário**: Usar credenciais do usuário (superadmin para admin completo)

---

## Credenciais Atuais

| Usuário | Secret Key | Buckets |
|---------|------------|---------|
| `tarcisio` | `CAmIzhdQysGaFIhRjLOtg` | Todos (superadmin) |
| `fina-app` | `z09DwR6NDzfBvmhky3ZKbw` | `fina` |
| `dev-team` | `ULCBV0uxrEmxNLFMOxpT` | `tmf-hub*` |

---

## Checklist para Nova Aplicação

- [ ] Criar bucket: `mc mb local/NOME-APP`
- [ ] Criar policy JSON
- [ ] Aplicar policy: `mc admin policy create`
- [ ] Criar usuário: `mc admin user add`
- [ ] Atribuir policy ao usuário
- [ ] Salvar credenciais em local seguro
- [ ] Configurar `.env` da aplicação
- [ ] Configurar `docker-compose.yml`
- [ ] Testar acesso (upload/download)
- [ ] Configurar script de backup

---

*Última atualização: 2026-02-05*
