# Comando: Analise de CVEs (Vulnerabilidades)

Analisa imagens Docker em busca de CVEs usando Trivy, cria issues no Jira para vulnerabilidades criticas/altas e sugere/executa correcoes.

## Pre-requisitos

- **Trivy** instalado: `brew install trivy`
- Imagens Docker buildadas localmente

## Argumentos

`$ARGUMENTS`

- Sem argumentos: Analisa todas as imagens do projeto
- `--image=<nome>`: Analisa uma imagem especifica
- `--severity=CRITICAL,HIGH,MEDIUM`: Define severidades a analisar (default: CRITICAL,HIGH)
- `--auto-fix`: Aplica correcoes automaticamente quando possivel
- `--skip-jira`: Nao cria issues no Jira
- `--report-only`: Apenas gera relatorio, sem acoes

## Imagens do Projeto

| Servico | Dockerfile | Imagem |
|---------|------------|--------|
| Tennis Tracking Backend | `backend/Dockerfile` | `tennis-tracking-backend:latest` |
| Tennis Tracking Frontend | `web/Dockerfile` | `tennis-tracking-frontend:latest` |

**Build para analise:**
```bash
docker build --platform linux/amd64 -f backend/Dockerfile -t tennis-tracking-backend:latest backend/
docker build --platform linux/amd64 -f web/Dockerfile -t tennis-tracking-frontend:latest web/
```

## Fluxo de Execucao

```
+-------------------------------------------------------------+
|  /cves [--image=X] [--auto-fix]                              |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|  1. Verificar pre-requisitos                                 |
|     - Trivy instalado?                                       |
|     - Imagens Docker existem?                                |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|  2. Executar analise Trivy                                   |
|     - Baixar/atualizar DB de vulnerabilidades                |
|     - Analisar cada imagem                                   |
|     - Coletar CVEs por severidade                            |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|  3. Processar resultados                                     |
|     - Agrupar por pacote/categoria                           |
|     - Identificar CVEs com fix disponivel                    |
|     - Filtrar falsos positivos conhecidos                    |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|  4. Gerar relatorio                                          |
|     - Resumo por severidade                                  |
|     - Detalhes das CVEs criticas                             |
|     - Recomendacoes de correcao                              |
+----------------------------+--------------------------------+
                             |
              +--------------+--------------+
              |                             |
         Sem CVEs                     Com CVEs
         criticas/altas               criticas/altas
              |                             |
              v                             v
+---------------------+    +----------------------------------+
|  5a. Exibir          |    |  5b. Criar issues no Jira        |
|      "Tudo OK!"      |    |      - Uma issue por categoria   |
|                      |    |      - Subtasks por pacote       |
+---------------------+    +----------------+-----------------+
                                            |
                                            v
                            +----------------------------------+
                            |  6. Executar correcoes           |
                            |     - Atualizar Dockerfile       |
                            |     - Atualizar dependencias     |
                            |     - Rebuild da imagem          |
                            +----------------------------------+
```

## Passos Detalhados

### 1. Verificar Pre-requisitos

```bash
# Verificar Trivy
which trivy || echo "Trivy nao instalado. Execute: brew install trivy"

# Verificar imagens
docker images tennis-tracking-backend:latest --format "{{.Repository}}:{{.Tag}}"
docker images tennis-tracking-frontend:latest --format "{{.Repository}}:{{.Tag}}"
```

Se imagem nao existir, buildar:
```bash
docker build --platform linux/amd64 -f backend/Dockerfile -t tennis-tracking-backend:latest backend/
```

### 2. Executar Analise Trivy

```bash
# Analise completa
trivy image --severity CRITICAL,HIGH --format json tennis-tracking-backend:latest > /tmp/trivy-tennis-tracking-backend.json
trivy image --severity CRITICAL,HIGH --format json tennis-tracking-frontend:latest > /tmp/trivy-tennis-tracking-frontend.json
```

### 3. Processar Resultados

Categorizar CVEs e mapear para epics do Jira:

| Categoria | Descricao | Epic Jira |
|-----------|-----------|-----------|
| OS/System | Pacotes do sistema operacional (apt, apk) | TT-14 (Infraestrutura) |
| Python | Dependencias Python (pip) | TT-14 (Infraestrutura) |
| Node/NPM | Dependencias Node.js | TT-14 (Infraestrutura) |
| Secrets | Credenciais expostas | TT-13 (Autenticacao) |
| Config | Configuracoes inseguras | TT-14 (Infraestrutura) |

Filtrar falsos positivos conhecidos:
- Templates de exemplo com credenciais ficticias
- CVEs do kernel nao aplicaveis em containers
- Pacotes nao utilizados em runtime

### 4. Gerar Relatorio

```
============================================================
RELATORIO DE VULNERABILIDADES (CVEs)
============================================================

Data: 2026-02-03 12:00:00
Ferramenta: Trivy v0.68.2

+------------------------------+----------+------+--------+-------+
| Imagem                       | Critical | High | Medium | Total |
+------------------------------+----------+------+--------+-------+
| tennis-tracking-backend:latest  |    1     |  42  |   --   |   43  |
| tennis-tracking-frontend:latest |    0     |  15  |   --   |   15  |
+------------------------------+----------+------+--------+-------+

============================================================
CVEs CRITICAS (Acao Imediata)
============================================================

1. CVE-XXXX-XXXXX | imagemagick | 8:7.1.1.43
   |- Severidade: CRITICAL
   |- Descricao: Arbitrary code execution via crafted XBM
   |- Fix disponivel: Sim (8:7.1.1.43-2)
   |- Recomendacao: Atualizar pacote

============================================================
CVEs HIGH (Por Categoria)
============================================================

Sistema Operacional (30 CVEs)
   |- linux-libc-dev: 25 CVEs (maioria kernel, baixo risco em container)
   |- libc-bin: 3 CVEs
   |- imagemagick: 2 CVEs

Python (8 CVEs)
   |- pillow: 3 CVEs (fix disponivel)
   |- cryptography: 2 CVEs (fix disponivel)
   |- requests: 3 CVEs

Node/NPM (4 CVEs)
   |- webpack: 2 CVEs
   |- postcss: 2 CVEs

============================================================
RECOMENDACOES
============================================================

1. [CRITICO] Atualizar imagemagick para versao patcheada
2. [HIGH] Atualizar dependencias Python com vulnerabilidades
3. [MEDIO] Considerar migrar para imagem Alpine (menos CVEs de OS)
4. [INFO] CVEs de kernel geralmente nao afetam containers

============================================================
```

### 5. Criar Issues no Jira

Para cada categoria com CVEs criticas/altas, criar issue usando `scripts/jira_helper.py`:

```bash
# Issue principal
python3 scripts/jira_helper.py create \
  --type "Tarefa" \
  --summary "fix(security): Corrigir CVEs criticas na imagem Docker tennis-tracking-backend" \
  --description "$(cat <<'EOF'
## Contexto
Analise de seguranca identificou **X CVEs criticas** e **Y CVEs altas** na imagem Docker tennis-tracking-backend.

## CVEs Identificadas

### Criticas
| CVE | Pacote | Versao Atual | Fix |
|-----|--------|--------------|-----|
| CVE-XXXX | package | 1.0.0 | 1.0.1 |

### Altas (Top 10)
| CVE | Pacote | Versao Atual | Fix |
|-----|--------|--------------|-----|
| CVE-YYYY | package | 2.0.0 | 2.0.1 |

## Criterios de Aceite
- [ ] CVEs criticas corrigidas
- [ ] CVEs altas com fix disponivel corrigidas
- [ ] Imagem rebuilded e testada
- [ ] Nova analise Trivy sem criticas

## Referencias
- [Trivy Report](link)
- [NVD Database](https://nvd.nist.gov/)

Detectado por: `/cves` | Trivy v0.68.2
EOF
)" \
  --priority "High" \
  --labels "security,docker,cve"
```

### 6. Executar Correcoes

#### 6.1 Correcoes Automaticas (--auto-fix)

**Atualizar dependencias Python:**
```bash
cd backend

# Atualizar pacotes com CVEs conhecidas
pip install --upgrade pillow cryptography requests

# Regenerar requirements.txt
pip freeze > requirements.txt

# Commitar mudancas
git add requirements.txt
git commit -m "fix(security): atualizar dependencias Python com CVEs [TH-XXX]"
```

**Atualizar backend/Dockerfile:**
```dockerfile
# Se ha patch disponivel, atualizar imagem base
FROM python:3.12-slim  # Verificar se ha versao mais recente

# Adicionar apt-get upgrade para pacotes do sistema
RUN apt-get update && apt-get upgrade -y && apt-get install -y ...
```

**Rebuild da imagem:**
```bash
docker build --platform linux/amd64 -f backend/Dockerfile -t tennis-tracking-backend:latest --no-cache backend/
```

#### 6.2 Correcoes Manuais (sugestoes)

```
============================================================
CORRECOES SUGERIDAS
============================================================

1. Atualizar requirements.txt (backend):
   pillow>=10.2.0  # Fix CVE-2024-XXXX
   cryptography>=42.0.0  # Fix CVE-2024-YYYY

2. Atualizar backend/Dockerfile (adicionar apos apt-get install):
   RUN apt-get update && apt-get upgrade -y

3. Considerar migracao para Alpine:
   FROM python:3.12-alpine
   # Reduz ~60 CVEs de OS

4. Adicionar .trivyignore para falsos positivos:
   # CVEs de kernel nao aplicaveis em container
   CVE-2013-7445
   CVE-2019-19449

============================================================
```

## Mapeamento CVE -> Correcao

| Tipo de CVE | Correcao | Auto-fix |
|-------------|----------|----------|
| Python package | `pip install --upgrade <pkg>` | Sim |
| Node package | `npm update <pkg>` | Sim |
| OS package (apt) | `apt-get upgrade` no Dockerfile | Sim |
| OS package (apk) | `apk upgrade` no Dockerfile | Sim |
| Base image | Atualizar versao no FROM | Manual |
| Secrets | Remover/rotacionar credencial | Manual |
| Config | Ajustar configuracao | Manual |

## Arquivo .trivyignore

Criar arquivo para ignorar falsos positivos:

```bash
# .trivyignore (na raiz do projeto)
# CVEs de kernel nao aplicaveis em containers
CVE-2013-7445
CVE-2019-19449
CVE-2019-19814

# Templates de exemplo (nao sao credenciais reais)
# push_config.py contem apenas exemplos
```

## Exemplo de Uso

### Analise Completa
```
/cves
```

### Apenas Imagem Especifica com Auto-fix
```
/cves --image=tennis-tracking-backend:latest --auto-fix
```

### Apenas Relatorio
```
/cves --report-only --severity=CRITICAL,HIGH,MEDIUM
```

## Output de Sucesso

```
============================================================
ANALISE DE CVEs CONCLUIDA
============================================================

Resumo:
   |- Imagens analisadas: 1
   |- CVEs criticas: 1 -> 0 (corrigidas)
   |- CVEs altas: 42 -> 34 (8 corrigidas)
   |- Issues criadas: 2

Issues Jira:
   |- TT-401: fix(security): Corrigir CVEs criticas na imagem Docker
   |   |- Status: To Do
   |   |- Link: https://trademarketingforce.atlassian.net/browse/TT-401
   |
   |- TT-402: fix(security): Atualizar dependencias Python
       |- Status: Done (auto-fix aplicado)
       |- Commit: abc1234

Correcoes Aplicadas:
   |- requirements.txt atualizado
   |- backend/Dockerfile: apt-get upgrade adicionado
   |- Imagem rebuilded: tennis-tracking-backend:latest

Proximos passos:
   - Verificar correcoes manuais pendentes em TT-401
   - Re-executar /cves para validar correcoes
   - Fazer deploy com /deploy

============================================================
```

## Regras

1. **SEMPRE** verificar se Trivy esta instalado antes de executar
2. **SEMPRE** gerar relatorio antes de criar issues
3. **SEMPRE** agrupar CVEs por categoria para evitar issues duplicadas
4. **SEMPRE** incluir link para NVD/CVE na descricao da issue
5. **NUNCA** ignorar CVEs criticas sem justificativa documentada
6. **NUNCA** commitar credenciais reais (verificar falsos positivos)
7. **NUNCA** aplicar auto-fix sem backup/commit anterior
8. CVEs de kernel em containers geralmente sao baixo risco
9. Priorizar CVEs com fix disponivel
10. Apos correcoes, sempre re-executar analise para validar
