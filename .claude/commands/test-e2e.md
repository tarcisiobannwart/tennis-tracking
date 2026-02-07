# Comando: Testes End-to-End (E2E)

Executa e gerencia testes end-to-end do Tennis Tracking com integracao ao Jira.

## Argumentos

`$ARGUMENTS` - Modulo ou issue Jira (ex: `clients`, `TT-123`, `--all`, `--create TT-145`)

Formato:
- `clients` - Roda testes E2E do modulo clientes
- `TT-123` - Roda testes vinculados a issue especifica
- `--all` - Roda todos os testes E2E
- `--create TT-145` - Cria testes E2E para a issue
- `--report` - Gera relatorio de cobertura E2E

## Mapeamento de Modulos e Epics

| Modulo | Epic Jira | Paginas Cobertas | Rota Base |
|--------|-----------|------------------|-----------|
| clients | TT-11 | Clients, ClientDetail, DataMigrations | /clients |
| hr | TT-12 | HR | /hr |
| finance | TT-13 | FinanceConciliation, FinanceCosts, FinanceReports, ExpenseManagement, Expenses, RecurringManagement, ForecastVsActual | /finance, /costs, /reports |
| crm | TT-14 | Opportunities, OpportunityDetail, Campaigns, Performance | /opportunities, /campaigns |
| infra | TT-15 | Functions, Logs, Observability, ServerOperations, Migrations | /functions, /logs, /observability |
| settings | TT-16 | Users, Security, Integrations, MenuAccess | /users, /security, /integrations |
| persons | - | Persons, Teams | /persons, /teams |
| projects | - | ProjectManagement | /projects |
| dashboard | - | Dashboard | / |
| communication | - | CommunicationDashboard | /communication |

## Portas e URLs

| Servico | Porta | URL |
|---------|-------|-----|
| Frontend | 11001 | http://localhost:11001 |
| Backend API | 11000 | http://localhost:11000 |
| PostgreSQL | 11002 | localhost:11002 |
| Redis | 11003 | localhost:11003 |
| API Docs | 11000 | http://localhost:11000/docs |

## Estrutura de Testes E2E

```
tests/
└── e2e/
    ├── README.md                # Documentacao dos testes E2E
    ├── conftest.py              # Fixtures compartilhadas
    ├── config.py                # Configuracoes (URLs, credenciais)
    ├── helpers/
    │   ├── api_client.py        # Client HTTP para API
    │   ├── auth.py              # Helper de autenticacao
    │   ├── database.py          # Helper para banco de dados
    │   └── assertions.py        # Assercoes customizadas
    ├── clients/                 # Testes do modulo Clientes (TT-11)
    │   ├── test_list_clients.py
    │   ├── test_client_detail.py
    │   └── test_client_crud.py
    ├── hr/                      # Testes do modulo RH (TT-12)
    │   ├── test_employees.py
    │   └── test_payroll.py
    ├── finance/                 # Testes do modulo Financeiro (TT-13)
    │   ├── test_conciliation.py
    │   ├── test_costs.py
    │   └── test_reports.py
    ├── crm/                     # Testes do modulo CRM (TT-14)
    │   ├── test_opportunities.py
    │   └── test_campaigns.py
    ├── infra/                   # Testes de Infraestrutura (TT-15)
    │   ├── test_functions.py
    │   ├── test_logs.py
    │   └── test_observability.py
    ├── settings/                # Testes de Configuracoes (TT-16)
    │   ├── test_users.py
    │   └── test_security.py
    ├── auth/                    # Testes de Autenticacao
    │   ├── test_login.py
    │   ├── test_permissions.py
    │   └── test_mfa.py
    └── health/                  # Testes de Health Check
        └── test_health.py
```

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────┐
│  1. Verificar ambiente                                   │
│     - Docker containers rodando?                         │
│     - Backend respondendo em :11000/health?               │
│     - Frontend respondendo em :11001?                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2. Preparar dados de teste                              │
│     - Seed do banco (se necessario)                      │
│     - Obter token de autenticacao                        │
│     - Configurar tenant de teste                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3. Executar testes do modulo                            │
│     pytest tests/e2e/{modulo}/ -v                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  4. Coletar resultados                                   │
│     - Testes passando/falhando                           │
│     - Screenshots de falhas (se Playwright)              │
│     - Tempo de execucao                                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  5. Atualizar Jira (se vinculado a issue)                │
│     - Adicionar comentario com resultados                │
│     - Mover para Done se todos passam                    │
│     - Mover para In Progress se falham                   │
└─────────────────────────────────────────────────────────┘
```

## Configuracao Base

### Config

```python
# tests/e2e/config.py

# URLs
API_BASE_URL = "http://localhost:11000"
FRONTEND_URL = "http://localhost:11001"
API_DOCS_URL = f"{API_BASE_URL}/docs"
HEALTH_URL = f"{API_BASE_URL}/health"

# Credenciais de teste
TEST_USER_EMAIL = "tarcisio@trademarketingforce.com"
TEST_USER_PASSWORD = "admin123"

# Timeouts
DEFAULT_TIMEOUT = 30  # segundos
API_TIMEOUT = 10      # segundos

# Database
DB_HOST = "localhost"
DB_PORT = 11002
DB_NAME = "tmf_hub_db"
DB_USER = "tmf_hub"
DB_PASSWORD = "tmf_hub_pass"
```

### Fixtures Compartilhadas

```python
# tests/e2e/conftest.py
import pytest
import requests
from tests.e2e.config import API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD

@pytest.fixture(scope="session")
def auth_token():
    """Obter token de autenticacao para testes."""
    response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )
    assert response.status_code == 200, f"Falha no login: {response.text}"
    return response.json()["access_token"]

@pytest.fixture(scope="session")
def api_client(auth_token):
    """Client HTTP autenticado."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
    })
    session.base_url = API_BASE_URL
    return session

@pytest.fixture(scope="session")
def check_services():
    """Verificar se os servicos estao rodando."""
    # Health check
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        assert r.status_code == 200
    except Exception as e:
        pytest.skip(f"Backend nao disponivel: {e}")

    # DB check
    try:
        r = requests.get(f"{API_BASE_URL}/health/db", timeout=5)
        assert r.status_code == 200
    except Exception as e:
        pytest.skip(f"Banco de dados nao disponivel: {e}")
```

### Helper de API

```python
# tests/e2e/helpers/api_client.py
import requests
from tests.e2e.config import API_BASE_URL, API_TIMEOUT

class TMFApiClient:
    """Client HTTP para testes E2E da API do TMF."""

    def __init__(self, token: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })
        self.base_url = API_BASE_URL

    def get(self, path: str, **kwargs):
        return self.session.get(
            f"{self.base_url}{path}",
            timeout=API_TIMEOUT,
            **kwargs,
        )

    def post(self, path: str, data: dict = None, **kwargs):
        return self.session.post(
            f"{self.base_url}{path}",
            json=data,
            timeout=API_TIMEOUT,
            **kwargs,
        )

    def put(self, path: str, data: dict = None, **kwargs):
        return self.session.put(
            f"{self.base_url}{path}",
            json=data,
            timeout=API_TIMEOUT,
            **kwargs,
        )

    def delete(self, path: str, **kwargs):
        return self.session.delete(
            f"{self.base_url}{path}",
            timeout=API_TIMEOUT,
            **kwargs,
        )
```

## Templates de Teste E2E

### Teste de Health Check

```python
# tests/e2e/health/test_health.py
import pytest
import requests
from tests.e2e.config import API_BASE_URL

class TestHealthCheck:
    """Testes de health check do Tennis Tracking."""

    def test_health_endpoint(self):
        """Endpoint /health deve retornar 200."""
        r = requests.get(f"{API_BASE_URL}/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"

    def test_health_db(self):
        """Endpoint /health/db deve retornar 200 se banco esta conectado."""
        r = requests.get(f"{API_BASE_URL}/health/db")
        assert r.status_code == 200

    def test_health_redis(self):
        """Endpoint /health/redis deve retornar 200 se Redis esta conectado."""
        r = requests.get(f"{API_BASE_URL}/health/redis")
        assert r.status_code == 200
```

### Teste de Autenticacao

```python
# tests/e2e/auth/test_login.py
import pytest
import requests
from tests.e2e.config import API_BASE_URL, TEST_USER_EMAIL, TEST_USER_PASSWORD

class TestLogin:
    """Testes de autenticacao do Tennis Tracking."""

    def test_login_sucesso(self):
        """Login com credenciais validas deve retornar token."""
        r = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_credenciais_invalidas(self):
        """Login com credenciais invalidas deve retornar 401."""
        r = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": "invalido@test.com", "password": "senha_errada"},
        )
        assert r.status_code == 401

    def test_acesso_sem_token(self):
        """Acessar endpoint protegido sem token deve retornar 401."""
        r = requests.get(f"{API_BASE_URL}/api/users")
        assert r.status_code in [401, 403]

    def test_acesso_com_token_invalido(self):
        """Acessar endpoint protegido com token invalido deve retornar 401."""
        r = requests.get(
            f"{API_BASE_URL}/api/users",
            headers={"Authorization": "Bearer token_invalido"},
        )
        assert r.status_code in [401, 403]

    def test_me_endpoint(self):
        """GET /api/auth/me deve retornar dados do usuario autenticado."""
        # Login
        login = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        token = login.json()["access_token"]

        # Me
        r = requests.get(
            f"{API_BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == TEST_USER_EMAIL
```

### Teste de CRUD (Modulo generico)

```python
# tests/e2e/clients/test_client_crud.py
import pytest
from tests.e2e.config import API_BASE_URL

class TestClientCRUD:
    """Testes CRUD do modulo de Clientes."""

    def test_listar_clientes(self, api_client, check_services):
        """GET /api/clients deve retornar lista de clientes."""
        r = api_client.get(f"{API_BASE_URL}/api/clients")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, (list, dict))

    def test_buscar_cliente_por_id(self, api_client, check_services):
        """GET /api/clients/:id deve retornar cliente especifico."""
        # Primeiro listar para pegar um ID
        lista = api_client.get(f"{API_BASE_URL}/api/clients")
        if lista.status_code == 200 and lista.json():
            items = lista.json() if isinstance(lista.json(), list) else lista.json().get("items", [])
            if items:
                client_id = items[0].get("id") or items[0].get("client_code")
                r = api_client.get(f"{API_BASE_URL}/api/clients/{client_id}")
                assert r.status_code in [200, 404]

    def test_endpoint_inexistente(self, api_client, check_services):
        """GET /api/clients/999999 deve retornar 404."""
        r = api_client.get(f"{API_BASE_URL}/api/clients/999999")
        assert r.status_code == 404
```

### Teste de Permissoes

```python
# tests/e2e/auth/test_permissions.py
import pytest
import requests
from tests.e2e.config import API_BASE_URL

class TestPermissions:
    """Testes de permissoes RBAC do Tennis Tracking."""

    def test_admin_acessa_users(self, api_client, check_services):
        """Admin deve conseguir acessar lista de usuarios."""
        r = api_client.get(f"{API_BASE_URL}/api/users")
        assert r.status_code == 200

    def test_listar_roles(self, api_client, check_services):
        """Deve listar roles disponiveis."""
        r = api_client.get(f"{API_BASE_URL}/api/users/roles")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Deve ter pelo menos os roles padrao
        role_names = [role["name"] for role in data]
        assert any("CEO" in name or "Admin" in name for name in role_names)
```

## Integracao com Jira

### Criar Testes para Issue

Ao receber `--create TT-145`:

1. Buscar issue no Jira via `scripts/jira_helper.py`:
   ```bash
   python scripts/jira_helper.py get TT-145
   ```

2. Analisar o tipo e modulo da issue

3. Gerar teste E2E baseado na descricao

4. Salvar em `tests/e2e/{modulo}/test_th_145.py`

5. Adicionar comentario na issue:
   ```bash
   python scripts/jira_helper.py comment TT-145 "Testes E2E criados: tests/e2e/{modulo}/test_th_145.py"
   ```

### Reportar Resultado para Issue

Ao vincular testes a uma issue:

```bash
# Executar testes e capturar resultado
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking
python -m pytest tests/e2e/{modulo}/ -v --tb=short 2>&1 | tee /tmp/test_result.txt

# Comentar resultado no Jira
python scripts/jira_helper.py comment TT-145 "$(cat /tmp/test_result.txt)"

# Se todos passaram, transicionar para Done
python scripts/jira_helper.py transition TT-145 31
```

## Comandos de Execucao

```bash
# Diretorio base
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking

# Verificar se ambiente esta rodando
curl -s http://localhost:11000/health | python -m json.tool

# Rodar todos os testes E2E
python -m pytest tests/e2e/ -v

# Rodar testes de um modulo
python -m pytest tests/e2e/clients/ -v
python -m pytest tests/e2e/auth/ -v
python -m pytest tests/e2e/health/ -v

# Rodar teste especifico
python -m pytest tests/e2e/clients/test_client_crud.py -v

# Com output detalhado
python -m pytest tests/e2e/ -v --tb=long

# Parar no primeiro erro
python -m pytest tests/e2e/ -v -x

# Com marcadores
python -m pytest tests/e2e/ -v -m "not slow"

# Gerar relatorio HTML
python -m pytest tests/e2e/ -v --html=tests/reports/e2e_report.html
```

## Verificacao de Ambiente

Antes de rodar testes E2E, verificar:

```bash
# 1. Containers Docker rodando
docker ps | grep tmf-hub

# 2. Backend respondendo
curl -s http://localhost:11000/health

# 3. Banco conectado
curl -s http://localhost:11000/health/db

# 4. Redis conectado
curl -s http://localhost:11000/health/redis

# 5. Frontend respondendo
curl -s -o /dev/null -w "%{http_code}" http://localhost:11001
```

Se algum servico nao estiver rodando:

```bash
# Subir stack completa
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking
docker compose up -d

# Verificar logs se houver erro
docker compose logs -f api
```

## Regras

1. **SEMPRE** verificar se o ambiente esta rodando antes de executar testes
2. **SEMPRE** usar credenciais de teste do config (nao hardcoded)
3. **NUNCA** modificar dados de producao
4. **SEMPRE** limpar dados criados durante testes (teardown)
5. **SEMPRE** usar `scripts/jira_helper.py` para operacoes no Jira
6. Testes devem ser idempotentes (rodar N vezes com mesmo resultado)
7. Testes nao devem depender de ordem de execucao
8. Usar fixtures do pytest para setup/teardown
9. Nomes de teste em portugues (docstrings)
10. Portas: 11000 (API), 11001 (frontend), 11002 (PostgreSQL), 11003 (Redis)
