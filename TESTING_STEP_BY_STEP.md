# 🧪 Guia Prático de Testes - Política de Retenção de Logs

## Fase 1: Validação da Migração

### Passo 1.1: Verificar se as tabelas existem

```bash
# Conectar ao PostgreSQL
psql -h localhost -U postgres -d zeus_db
```

```sql
-- Listar todas as tabelas necessárias
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('TB_AUTH_ATTEMPT', 'TB_SESSION')
ORDER BY table_name;
```

**Resultado esperado**:
```
    table_name
─────────────────
 TB_AUTH_ATTEMPT
 TB_SESSION
```

### Passo 1.2: Verificar colunas de timestamp

```sql
-- Verificar colunas de TB_AUTH_ATTEMPT
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'TB_AUTH_ATTEMPT'
  AND column_name IN ('ATTEMPTED_AT', 'EMAIL_HASH', 'SOURCE_IP')
ORDER BY column_name;
```

**Resultado esperado**:
```
   column_name   │           data_type           │ is_nullable
─────────────────┼───────────────────────────────┼─────────────
 ATTEMPTED_AT    │ timestamp with time zone      │ Yes
 EMAIL_HASH      │ character varying             │ No
 SOURCE_IP       │ character varying             │ No
```

```sql
-- Verificar colunas de TB_SESSION
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'TB_SESSION'
  AND column_name IN ('CREATED_AT', 'DELETED_AT')
ORDER BY column_name;
```

**Resultado esperado**:
```
   column_name   │           data_type           │ is_nullable
─────────────────┼───────────────────────────────┼─────────────
 CREATED_AT      │ timestamp with time zone      │ No
 DELETED_AT      │ timestamp with time zone      │ Yes
```

### Passo 1.3: Verificar se os índices foram criados

```sql
-- Listar índices para TB_AUTH_ATTEMPT
SELECT indexname FROM pg_indexes
WHERE tablename = 'TB_AUTH_ATTEMPT'
  AND indexname LIKE '%ATTEMPTED%';
```

**Resultado esperado**:
```
            indexname
──────────────────────────────────
 IX_TB_AUTH_ATTEMPT_ATTEMPTED_AT
```

```sql
-- Listar índices para TB_SESSION
SELECT indexname FROM pg_indexes
WHERE tablename = 'TB_SESSION'
  AND indexname LIKE '%CREATED%';
```

**Resultado esperado**:
```
              indexname
──────────────────────────────────────────
 IX_TB_SESSION_CREATED_AT_DELETED_AT
```

### Passo 1.4: Executar a migração (se ainda não foi executada)

```bash
# Na raiz do projeto ou no diretório onde está a migração
psql -h localhost -U postgres -d zeus_db \
  -f database/migrations/V010__log_retention_setup.sql
```

**Resultado esperado**: Nenhum erro, mensagens de NOTICE no console

---

## Fase 2: Validação das Funções PostgreSQL

### Passo 2.1: Verificar se as funções existem

```sql
-- Listar funções de retenção
SELECT routine_name FROM information_schema.routines
WHERE routine_name LIKE '%log_retention%'
ORDER BY routine_name;
```

**Resultado esperado**:
```
        routine_name
──────────────────────────────
 execute_log_retention_cleanup
 get_log_retention_dryrun
```

### Passo 2.2: Testar a função de dry-run

```sql
-- Executar dry-run com 90 dias
SELECT * FROM get_log_retention_dryrun(90);
```

**Resultado esperado**:
```
    table_name    │ would_delete_count │ oldest_record │       cutoff_date
──────────────────┼────────────────────┼───────────────┼─────────────────
 TB_AUTH_ATTEMPT  │        0           │    NULL       │ 2026-02-24...
 TB_SESSION       │        0           │    NULL       │ 2026-02-24...
```

(Se não há dados antigos, seria 0 em ambas)

### Passo 2.3: Criar dados de teste para validar cleanup

```sql
-- Inserir um auth_attempt antigo (mais de 90 dias)
INSERT INTO TB_AUTH_ATTEMPT (EMAIL_HASH, SOURCE_IP, SUCCESS, BLOCKED, ATTEMPTED_AT)
VALUES (
  'test_old_hash@example.com',
  '192.168.1.100',
  FALSE,
  FALSE,
  NOW() - INTERVAL '120 days'
);

-- Inserir um auth_attempt recente (menos de 90 dias)
INSERT INTO TB_AUTH_ATTEMPT (EMAIL_HASH, SOURCE_IP, SUCCESS, BLOCKED, ATTEMPTED_AT)
VALUES (
  'test_recent_hash@example.com',
  '192.168.1.101',
  TRUE,
  FALSE,
  NOW() - INTERVAL '10 days'
);

-- Confirmar os inserts
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT;
SELECT MIN(ATTEMPTED_AT), MAX(ATTEMPTED_AT) FROM TB_AUTH_ATTEMPT;
```

**Resultado esperado**:
```
Adicionou 2 registros
 MIN(ATTEMPTED_AT)      │      MAX(ATTEMPTED_AT)
────────────────────────┼────────────────────────
 2025-12-26 10:30... (antigo) │ 2026-05-15 10:30... (recente)
```

### Passo 2.4: Testar dry-run novamente

```sql
-- Agora deve mostrar 1 registro para deletar
SELECT * FROM get_log_retention_dryrun(90);
```

**Resultado esperado**:
```
    table_name    │ would_delete_count │       oldest_record        │       cutoff_date
──────────────────┼────────────────────┼──────────────────────────┼──────────────────
 TB_AUTH_ATTEMPT  │        1           │ 2025-12-26 10:30... (old) │ 2026-02-24...
 TB_SESSION       │        0           │    NULL                   │ 2026-02-24...
```

---

## Fase 3: Testar Execução de Cleanup via SQL

### Passo 3.1: Executar o cleanup

```sql
-- Executar cleanup
SELECT * FROM execute_log_retention_cleanup(90);
```

**Resultado esperado**:
```
    table_name    │ rows_affected │       cutoff_date         │      operation_id
──────────────────┼───────────────┼──────────────────────────┼──────────────────────
 TB_AUTH_ATTEMPT  │       1       │ 2026-02-24 10:30:00... │ 550e8400-e29b-41d4...
 TB_SESSION       │       0       │ 2026-02-24 10:30:00... │ 550e8400-e29b-41d4...
```

### Passo 3.2: Verificar que o registro foi deletado

```sql
-- Contar registros
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT;
```

**Resultado esperado**:
```
 count
───────
   1
```

(O registro antigo foi deletado, apenas o recente permanece)

```sql
-- Verificar qual registro permanece
SELECT EMAIL_HASH, ATTEMPTED_AT FROM TB_AUTH_ATTEMPT;
```

**Resultado esperado**:
```
       EMAIL_HASH          │       ATTEMPTED_AT
──────────────────────────┼──────────────────────
 test_recent_hash@example │ 2026-05-15 10:30...
```

### Passo 3.3: Testar soft-delete de sessões

```sql
-- Criar sessões antigas para teste
INSERT INTO TB_SESSION (USER_ID, SOURCE_IP, USER_AGENT, EXPIRES_AT, CREATED_AT)
SELECT 
  USER_UUID,
  '192.168.1.50',
  'Mozilla/5.0 Test',
  NOW() - INTERVAL '60 days',
  NOW() - INTERVAL '120 days'
FROM TB_USER
LIMIT 1;

-- Criar sessão recente
INSERT INTO TB_SESSION (USER_ID, SOURCE_IP, USER_AGENT, EXPIRES_AT, CREATED_AT)
SELECT 
  USER_UUID,
  '192.168.1.51',
  'Mozilla/5.0 Test Recent',
  NOW() + INTERVAL '7 days',
  NOW() - INTERVAL '10 days'
FROM TB_USER
LIMIT 1;

-- Contar antes do cleanup
SELECT COUNT(*) as total_sessions,
       COUNT(*) FILTER (WHERE DELETED_AT IS NULL) as active_sessions
FROM TB_SESSION;
```

**Resultado esperado**:
```
 total_sessions │ active_sessions
────────────────┼─────────────────
      X+2       │      X
```

(Duas novas sessões, ambas ativas)

### Passo 3.4: Executar cleanup novamente

```sql
-- Cleanup com 90 dias
SELECT * FROM execute_log_retention_cleanup(90);
```

**Resultado esperado**:
```
    table_name    │ rows_affected │       cutoff_date         │      operation_id
──────────────────┼───────────────┼──────────────────────────┼──────────────────────
 TB_AUTH_ATTEMPT  │       0       │ 2026-02-24 10:30:00... │ 550e8400-xxxx-xxxx...
 TB_SESSION       │       1       │ 2026-02-24 10:30:00... │ 550e8400-xxxx-xxxx...
```

(1 sessão antiga foi soft-deleted)

### Passo 3.5: Verificar soft-delete

```sql
-- Contar sessões ativas
SELECT COUNT(*) FILTER (WHERE DELETED_AT IS NULL) as active_sessions
FROM TB_SESSION;
```

**Resultado esperado**:
```
 active_sessions
─────────────────
      X+1
```

(Uma sessão foi soft-deletada, apenas a recente permanece ativa)

```sql
-- Ver detalhes das sessões
SELECT SESSION_UUID, CREATED_AT, DELETED_AT, SOURCE_IP
FROM TB_SESSION
WHERE CREATED_AT > NOW() - INTERVAL '200 days'
ORDER BY CREATED_AT;
```

**Resultado esperado**:
```
      SESSION_UUID          │      CREATED_AT        │     DELETED_AT      │  SOURCE_IP
──────────────────────────┼──────────────────────┼──────────────────────┼────────────
 old-session-uuid-xxx      │ 2025-12-26 10:30...  │ 2026-05-25 10:45... │ 192.168.1.50
 recent-session-uuid-xxx   │ 2026-05-15 10:30...  │        NULL          │ 192.168.1.51
```

---

## Fase 4: Testar via Python (Serviço)

### Passo 4.1: Preparar ambiente Python

```bash
# Entrar no diretório do backend
cd apps/backend

# Verificar variáveis de ambiente
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"

# Se não estiverem configuradas, defina:
export POSTGRES_HOST=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=sua_senha
export POSTGRES_DB=zeus_db
```

### Passo 4.2: Testar com Python - Mostrar Info

```bash
# Mostrar informações da política
python examples/retention_cleanup_example.py --info
```

**Resultado esperado**:
```
================================================================================
Retention Policy Information
================================================================================

Retention Period: 90 days
Compliance Standard: LGPD Art. 7 (Data Protection)
Operation Mode: HARD DELETE for TB_AUTH_ATTEMPT | SOFT DELETE for TB_SESSION

Tables Under Retention:

  TB_AUTH_ATTEMPT:
    Timestamp Column: ATTEMPTED_AT
    Description: Authentication attempt logs - LGPD Art. 7

  TB_SESSION:
    Timestamp Column: CREATED_AT
    Description: User session records - LGPD Art. 7
    Soft Delete: True

Current Cutoff Date: 2026-02-24T10:30:00+00:00
  (Records older than this will be cleaned up)
```

### Passo 4.3: Testar com Python - Dry-Run

```bash
# Fazer dry-run (não modifica dados)
python examples/retention_cleanup_example.py --dry-run
```

**Resultado esperado**:
```
================================================================================
DRY-RUN: Log Retention Cleanup
================================================================================

Retention Period: 90 days
Querying database for records that would be deleted...

Cutoff Date: 2026-02-24T10:30:00+00:00

TB_AUTH_ATTEMPT:
  Records that would be deleted: 0
  No records to delete

TB_SESSION:
  Records that would be deleted: 1
  Oldest record timestamp: 2025-12-26T10:30:00+00:00

TOTAL RECORDS TO DELETE: 1

⚠ 1 records are eligible for cleanup.
  Run with --execute flag to perform actual cleanup.
```

### Passo 4.4: Testar com Python - Execute

```bash
# Executar cleanup de verdade
python examples/retention_cleanup_example.py --execute
```

**Resultado esperado**:
```
================================================================================
EXECUTING: Log Retention Cleanup
================================================================================

Retention Period: 90 days
Starting cleanup operation...

Operation ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Status: SUCCESS
Cutoff Date: 2026-02-24T10:30:00+00:00

TB_AUTH_ATTEMPT:
  Rows deleted/updated: 0

TB_SESSION:
  Rows deleted/updated: 1

TOTAL ROWS PROCESSED: 1

✓ Cleanup completed successfully!
```

### Passo 4.5: Testar com período customizado

```bash
# Limpar registros com apenas 7 dias (para teste)
python examples/retention_cleanup_example.py --dry-run --days 7
```

**Resultado esperado**: Mostra o que seria deletado com 7 dias

```bash
# Executar com 7 dias
python examples/retention_cleanup_example.py --execute --days 7
```

---

## Fase 5: Validação de Integridade de Dados

### Passo 5.1: Verificar dados não foram corrompidos

```bash
# Conectar ao PostgreSQL
psql -h localhost -U postgres -d zeus_db
```

```sql
-- Contar registros totais (incluindo deletados)
SELECT 'TB_AUTH_ATTEMPT' as table_name, COUNT(*) as total
FROM TB_AUTH_ATTEMPT
UNION ALL
SELECT 'TB_SESSION', COUNT(*)
FROM TB_SESSION;
```

**Resultado esperado**:
```
      table_name      │ total
──────────────────────┼────────
 TB_AUTH_ATTEMPT      │    1
 TB_SESSION           │    X
```

### Passo 5.2: Verificar integridade referencial

```sql
-- Verificar que não há sessões órfãs
SELECT COUNT(*) FROM TB_SESSION
WHERE USER_ID NOT IN (SELECT USER_UUID FROM TB_USER);
```

**Resultado esperado**:
```
 count
───────
   0
```

(Nenhuma sessão órfã)

### Passo 5.3: Verificar soft-deletes estão corretos

```sql
-- Verificar que registros soft-deletados têm DELETED_AT
SELECT COUNT(*) 
FROM TB_SESSION
WHERE DELETED_AT IS NOT NULL AND DELETED_AT < NOW();
```

**Resultado esperado**:
```
 count
───────
   1
```

(1 registro foi soft-deletado, conforme esperado)

---

## Fase 6: Validação de Performance

### Passo 6.1: Medir tempo de execução

```bash
# Medir tempo com dry-run
time python examples/retention_cleanup_example.py --dry-run
```

**Esperado**: < 5 segundos

### Passo 6.2: Medir tempo de cleanup

```bash
# Medir tempo de execução
time python examples/retention_cleanup_example.py --execute
```

**Esperado**: < 10 segundos (para volumes normais)

### Passo 6.3: Verificar tamanho de tabelas

```sql
-- Tamanho das tabelas
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename IN ('TB_AUTH_ATTEMPT', 'TB_SESSION')
ORDER BY tablename;
```

**Resultado esperado**:
```
     tablename      │  size
───────────────────┼────────
 TB_AUTH_ATTEMPT   │  48 kB
 TB_SESSION        │ 120 kB
```

---

## Fase 7: Limpeza de Dados de Teste

### Passo 7.1: Remover dados de teste

```sql
-- Remover registros de teste
DELETE FROM TB_AUTH_ATTEMPT
WHERE EMAIL_HASH LIKE 'test_%';

-- Remover sessões de teste (opcional - remover hard delete)
DELETE FROM TB_SESSION
WHERE SOURCE_IP = '192.168.1.50' OR SOURCE_IP = '192.168.1.51';

-- Confirmar limpeza
SELECT COUNT(*) FROM TB_AUTH_ATTEMPT;
SELECT COUNT(*) FROM TB_SESSION;
```

---

## ✅ Checklist Final de Testes

- [ ] **Migração**: Tabelas e colunas existem
- [ ] **Índices**: Criados com sucesso
- [ ] **Funções SQL**: Existem e funcionam
- [ ] **Dry-run SQL**: Mostra contagem correta
- [ ] **Execute SQL**: Deleta registros antigos
- [ ] **Soft-delete**: Sessions marcadas com DELETED_AT
- [ ] **Python Info**: Mostra política corretamente
- [ ] **Python Dry-run**: Valida sem modificar
- [ ] **Python Execute**: Executa cleanup com sucesso
- [ ] **Integridade**: Nenhuma corrupção de dados
- [ ] **Performance**: Executa em menos de 10s
- [ ] **Dados de teste**: Removidos

---

## 🔧 Troubleshooting

### Problema: "function does not exist"

**Solução**:
```sql
-- Verificar se a função foi criada
SELECT routine_name FROM information_schema.routines
WHERE routine_name LIKE '%cleanup%';

-- Se não existe, execute a migração novamente
psql -h localhost -U postgres -d zeus_db \
  -f database/migrations/V010__log_retention_setup.sql
```

### Problema: "column ... does not exist"

**Solução**:
```sql
-- Verificar estrutura da tabela
\d TB_AUTH_ATTEMPT
\d TB_SESSION

-- Se colunas faltam, verificar V001 e migrações anteriores
```

### Problema: Python não conecta ao banco

**Solução**:
```bash
# Verificar variáveis de ambiente
env | grep POSTGRES

# Testar conexão PostgreSQL
psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"
```

### Problema: Permission denied

**Solução**:
```sql
-- Conceder permissão ao usuário
GRANT EXECUTE ON FUNCTION execute_log_retention_cleanup TO postgres;
GRANT EXECUTE ON FUNCTION get_log_retention_dryrun TO postgres;
```

---

## 📊 Exemplo de Fluxo Completo

```bash
# 1. Mostrar política
python examples/retention_cleanup_example.py --info

# 2. Validar o que seria deletado
python examples/retention_cleanup_example.py --dry-run

# 3. Se tudo OK, executar
python examples/retention_cleanup_example.py --execute

# 4. Verificar logs (se houver logging)
tail -f logs/app.log | grep "log_retention"
```

---

**Tempo estimado para todo o teste**: ~30 minutos  
**Sem criar arquivos**: ✅ Apenas testes no banco e CLI
