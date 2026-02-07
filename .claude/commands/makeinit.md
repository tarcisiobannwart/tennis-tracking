# Comando: Inicializar/Gerenciar Banco de Dados

Gerencia o banco de dados MongoDB do Tennis Tracking via Docker.

> **NOTA**: O Tennis Tracking usa **MongoDB**. Comandos PostgreSQL (pg_dump, psql) devem ser adaptados para MongoDB (mongodump, mongorestore, mongo shell).

## Argumentos

`$ARGUMENTS` - Acao a executar (ex: `dump`, `restore`, `seed`, `reset`, `info`, `export-seed`)

Formato:
- Vazio ou `info` - Mostra informacoes do banco
- `dump` - Cria backup completo do banco
- `restore` - Restaura ultimo backup
- `restore <arquivo>` - Restaura backup especifico
- `seed` - Popula dados iniciais (sem recriar tabelas)
- `reset` - Reset completo (DROP + CREATE + SEED) - CUIDADO!
- `export-seed` - Exporta dados atuais como seed
- `migrate` - Executa migrations pendentes
- `tables` - Lista todas as tabelas e contagem de registros

## Configuracao do Banco

| Parametro | Valor |
|-----------|-------|
| Container | `tmf-hub-postgres` |
| Database | `tmf_hub_db` |
| Usuario | `tmf_hub` |
| Senha | `tmf_hub_pass` |
| Porta | `11002` |
| Imagem | PostgreSQL 15 |

## Scripts Existentes

O TMF ja possui scripts para gerenciamento do banco:

```
scripts/
├── init-db.sh                # Script bash principal
├── run-migrations.sh         # Executor de migrations
├── migrations/               # SQL migrations manuais
│   ├── 000_create_migrations_table.sql
│   ├── 001_add_clients_table.sql
│   └── 002_add_email_notification_columns.sql
├── sql/                      # Scripts SQL auxiliares
└── db/                       # Scripts de banco auxiliares

backend/app/scripts/
├── init_database.py          # Inicializacao via Python
└── create_admin.py           # Criar usuario admin
```

### Makefile Existente

```bash
make db-init        # Modo interativo
make db-auto        # Automatico (sem perguntas)
make db-reset       # Reset completo (CUIDADO!)
make db-info        # Informacoes do banco
make db-seed        # Popular dados iniciais
make db-connect     # Conectar via psql
make db-backup      # Backup automatico
make db-restore     # Restaurar ultimo backup
```

## Fluxo de Execucao

```
┌─────────────────────────────────────────────────────────┐
│  1. Verificar container PostgreSQL                       │
│     docker ps | grep tmf-hub-postgres                    │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2. Executar acao solicitada                             │
│     (dump, restore, seed, reset, info, etc.)             │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3. Validar resultado                                    │
│     - Verificar tabelas existem                          │
│     - Verificar dados de seed                            │
│     - Verificar migrations aplicadas                     │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  4. Reportar resultado                                   │
│     - Tabelas criadas/existentes                         │
│     - Registros inseridos/existentes                     │
│     - Warnings se aplicavel                              │
└─────────────────────────────────────────────────────────┘
```

## Comandos por Acao

### info - Informacoes do Banco

```bash
# Via Makefile
make db-info

# Via script
./scripts/init-db.sh info

# Via Docker direto
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\dt+"

# Contagem de registros por tabela
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT
  schemaname,
  relname as tabela,
  n_live_tup as registros
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
"

# Tamanho do banco
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT pg_size_pretty(pg_database_size('tmf_hub_db')) as tamanho;
"

# Migrations aplicadas
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT * FROM schema_migrations ORDER BY applied_at;
"
```

### dump - Backup Completo

```bash
# Via Makefile (salva em backups/)
make db-backup

# Via Docker direto
mkdir -p /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups
docker exec tmf-hub-postgres pg_dump -U tmf_hub tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Dump apenas schema (sem dados)
docker exec tmf-hub-postgres pg_dump -U tmf_hub --schema-only tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/schema_$(date +%Y%m%d).sql

# Dump apenas dados (sem schema)
docker exec tmf-hub-postgres pg_dump -U tmf_hub --data-only tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/data_$(date +%Y%m%d).sql

# Dump de tabela especifica
docker exec tmf-hub-postgres pg_dump -U tmf_hub -t users tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/users_$(date +%Y%m%d).sql

# Dump compactado
docker exec tmf-hub-postgres pg_dump -U tmf_hub -Fc tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/backup_$(date +%Y%m%d).dump
```

### restore - Restaurar Backup

```bash
# Via Makefile (restaura ultimo backup)
make db-restore

# Via Makefile (arquivo especifico)
make db-restore FILE=backups/backup_20260203.sql

# Via Docker direto (SQL plain)
docker exec -i tmf-hub-postgres psql -U tmf_hub tmf_hub_db < /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/backup_20260203.sql

# Via Docker direto (formato custom .dump)
docker exec -i tmf-hub-postgres pg_restore -U tmf_hub -d tmf_hub_db --clean < /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/backup_20260203.dump

# Restaurar apenas uma tabela
docker exec -i tmf-hub-postgres psql -U tmf_hub tmf_hub_db < /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/users_20260203.sql
```

### seed - Popular Dados Iniciais

```bash
# Via Makefile
make db-seed

# Via script bash
./scripts/init-db.sh seed

# Via Python
docker exec tmf-hub-api python -m app.scripts.init_database --seed-only

# Ou diretamente (se Python estiver local)
cd /Volumes/DcokerSSD/DEVELOP/tennis-tracking/backend
python app/scripts/init_database.py --seed-only
```

**Dados de seed padrao:**
- 86 permissoes do sistema
- 9 roles hierarquicos (CEO, Gerente, Dev Pleno, Dev Jr, PJ, etc.)
- Usuario admin inicial (tarcisio@trademarketingforce.com / admin123)

### reset - Reset Completo

**ATENCAO: Esta acao apaga todos os dados!**

```bash
# Via Makefile (pede confirmacao)
make db-reset

# Via script
./scripts/init-db.sh reset

# Via Python
docker exec tmf-hub-api python -m app.scripts.init_database --reset

# Via Docker direto (manual)
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO tmf_hub;
GRANT ALL ON SCHEMA public TO public;
"
# Depois recriar tabelas e seed
./scripts/init-db.sh auto
```

### export-seed - Exportar Dados como Seed

Exporta os dados atuais do banco para usar como seed em outros ambientes:

```bash
# Exportar tabelas de configuracao (roles, permissions, etc.)
docker exec tmf-hub-postgres pg_dump -U tmf_hub \
  --data-only \
  --column-inserts \
  -t roles \
  -t permissions \
  -t role_permissions \
  -t schema_migrations \
  tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/sql/seed_config.sql

# Exportar usuarios (sem senhas sensiveis)
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
COPY (
  SELECT id, email, full_name, department, phone, role_id, is_active, created_at
  FROM users
) TO STDOUT WITH CSV HEADER;
" > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/sql/users_export.csv

# Exportar clientes
docker exec tmf-hub-postgres pg_dump -U tmf_hub \
  --data-only \
  --column-inserts \
  -t clients \
  tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/sql/seed_clients.sql

# Exportar tudo relevante para seed
docker exec tmf-hub-postgres pg_dump -U tmf_hub \
  --data-only \
  --column-inserts \
  -t roles \
  -t permissions \
  -t role_permissions \
  -t users \
  -t clients \
  -t tenants \
  -t schema_migrations \
  tmf_hub_db > /Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/sql/seed_complete.sql
```

### migrate - Executar Migrations

```bash
# Via script dedicado
./scripts/run-migrations.sh local

# Em producao
DB_PASS=senha_producao ./scripts/run-migrations.sh prod

# Verificar migrations aplicadas
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT version, name, applied_at
FROM schema_migrations
ORDER BY version;
"

# Aplicar migration especifica manualmente
docker exec -i tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db < scripts/migrations/002_add_email_notification_columns.sql
```

### tables - Listar Tabelas

```bash
# Listar todas as tabelas
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\dt"

# Listar com tamanho
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\dt+"

# Contagem de registros detalhada
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT
  t.table_name,
  (SELECT count(*) FROM information_schema.columns c WHERE c.table_name = t.table_name) as colunas,
  (xpath('/row/cnt/text()', xml_count))[1]::text::int as registros
FROM information_schema.tables t
CROSS JOIN LATERAL (
  SELECT query_to_xml(format('SELECT count(*) as cnt FROM %I.%I', t.table_schema, t.table_name), false, true, '') as xml_count
) x
WHERE t.table_schema = 'public'
ORDER BY t.table_name;
"

# Estrutura de uma tabela especifica
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\d+ users"
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\d+ clients"
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "\d+ tenants"
```

## Tabelas Principais do TMF

| Tabela | Descricao | Modulo |
|--------|-----------|--------|
| `users` | Usuarios do sistema | Auth |
| `roles` | Papeis (CEO, Gerente, Dev, etc.) | Auth |
| `permissions` | Permissoes do sistema (86 total) | Auth |
| `role_permissions` | Relacao N:N roles-permissions | Auth |
| `tenants` | Tenants (clientes multi-tenant) | Core |
| `tenant_secrets` | Secrets criptografados por tenant | Core |
| `tenant_tokens` | Tokens de API por tenant | Core |
| `clients` | Clientes da TMF | Clientes |
| `jira_projects` | Projetos Jira sincronizados | Jira |
| `tempo_worklogs` | Worklogs do Tempo | Jira |
| `aws_costs` | Custos AWS | Custos |
| `invoices` | Notas fiscais | Contabilidade |
| `payments` | Pagamentos | Contabilidade |
| `cost_allocations` | Alocacao de custos | Contabilidade |
| `employees` | Funcionarios | RH |
| `payslips` | Holerites | RH |
| `payrolls` | Folhas de pagamento | RH |
| `contaazul_tokens` | Tokens ContaAzul | Integracoes |
| `contaazul_syncs` | Sincronizacoes ContaAzul | Integracoes |
| `schema_migrations` | Controle de migrations | Sistema |

## Criar Nova Migration

### Passo a Passo

1. Verificar ultima migration:
```bash
ls -la /Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/migrations/
```

2. Criar arquivo com proximo numero:
```bash
# Exemplo: scripts/migrations/003_descricao.sql
```

3. Usar padrao idempotente:
```sql
-- Migration: 003 - Descricao da alteracao
-- Data: 2026-02-03

-- Adicionar coluna (idempotente)
ALTER TABLE clients ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS address TEXT;

-- Criar indice (idempotente)
CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone);

-- Registrar migration
INSERT INTO schema_migrations (version, name)
SELECT '003', 'descricao_alteracao'
WHERE NOT EXISTS (
  SELECT 1 FROM schema_migrations WHERE version = '003'
);
```

4. Aplicar migration:
```bash
./scripts/run-migrations.sh local
```

5. Verificar:
```bash
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 5;
"
```

## Troubleshooting

### Container nao inicia

```bash
# Verificar status
docker ps -a | grep tmf-hub-postgres

# Ver logs
docker logs tmf-hub-postgres

# Reiniciar
docker restart tmf-hub-postgres

# Se nao resolver, recriar
docker compose down
docker compose up -d postgres
```

### Conexao recusada

```bash
# Verificar se porta 11002 esta aberta
lsof -i :11002

# Testar conexao direta
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "SELECT 1"

# Verificar pg_hba.conf
docker exec tmf-hub-postgres cat /var/lib/postgresql/data/pg_hba.conf
```

### Tabelas nao existem

```bash
# Executar init completo
make db-auto

# Ou via script
./scripts/init-db.sh auto
```

### Permissoes insuficientes

```bash
# Verificar owner do banco
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
SELECT datname, datdba, pg_catalog.pg_get_userbyid(datdba) as owner
FROM pg_catalog.pg_database
WHERE datname = 'tmf_hub_db';
"

# Dar permissoes
docker exec tmf-hub-postgres psql -U tmf_hub -d tmf_hub_db -c "
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tmf_hub;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tmf_hub;
"
```

## Regras

1. **SEMPRE** usar Docker para acessar o banco (`docker exec tmf-hub-postgres`)
2. **NUNCA** conectar diretamente ao banco de producao sem confirmacao
3. **SEMPRE** fazer backup antes de operacoes destrutivas (reset, drop)
4. **SEMPRE** usar `IF NOT EXISTS` / `IF EXISTS` em migrations para idempotencia
5. **NUNCA** alterar `scripts/init-db.sh` ou `backend/app/scripts/init_database.py` sem necessidade
6. Backups salvos em `/Volumes/DcokerSSD/DEVELOP/tennis-tracking/backups/`
7. Migrations em `/Volumes/DcokerSSD/DEVELOP/tennis-tracking/scripts/migrations/`
8. Container: `tmf-hub-postgres`, DB: `tmf_hub_db`, User: `tmf_hub`, Porta: `11002`
