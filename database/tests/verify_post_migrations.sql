\set ON_ERROR_STOP on

BEGIN;

CREATE TEMP TABLE verification_results (
    check_name TEXT NOT NULL,
    ok BOOLEAN NOT NULL,
    details TEXT NOT NULL
);

INSERT INTO verification_results (check_name, ok, details)
SELECT
    'TB_LOG does not exist',
    to_regclass('public.tb_log') IS NULL,
    CASE
        WHEN to_regclass('public.tb_log') IS NULL THEN 'OK'
        ELSE 'Found table public.tb_log'
    END;

INSERT INTO verification_results (check_name, ok, details)
SELECT
    'Unique session index exists',
    EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'tb_session'
          AND lower(indexdef) LIKE '%create unique index%'
          AND lower(indexdef) LIKE '%on public.tb_session%'
          AND lower(indexdef) LIKE '%(user_id)%'
          AND lower(indexdef) LIKE '%where (invalidated_at is null)%'
    ),
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND tablename = 'tb_session'
              AND lower(indexdef) LIKE '%create unique index%'
              AND lower(indexdef) LIKE '%on public.tb_session%'
              AND lower(indexdef) LIKE '%(user_id)%'
              AND lower(indexdef) LIKE '%where (invalidated_at is null)%'
        ) THEN 'OK'
        ELSE 'Missing unique partial index on TB_SESSION(USER_ID) WHERE INVALIDATED_AT IS NULL'
    END;

INSERT INTO verification_results (check_name, ok, details)
SELECT
    'RLS enabled on critical tables',
    (
        SELECT COUNT(*)
        FROM pg_class c
        JOIN pg_namespace n
          ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname IN ('tb_user', 'tb_session', 'tb_consent_log')
          AND c.relrowsecurity = true
    ) = 3,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM pg_class c
            JOIN pg_namespace n
              ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname IN ('tb_user', 'tb_session', 'tb_consent_log')
              AND c.relrowsecurity = true
        ) = 3 THEN 'OK'
        ELSE 'Expected RLS enabled on TB_USER, TB_SESSION, and TB_CONSENT_LOG'
    END;

INSERT INTO verification_results (check_name, ok, details)
SELECT
    'dba_role has BYPASSRLS',
    EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'dba_role'
          AND rolbypassrls = true
    ),
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM pg_roles
            WHERE rolname = 'dba_role'
              AND rolbypassrls = true
        ) THEN 'OK'
        ELSE 'Role dba_role missing or does not have BYPASSRLS'
    END;

WITH expected_columns AS (
    SELECT 'reset_uuid'::text AS column_name, 'uuid'::text AS data_type, NULL::int AS char_len
    UNION ALL
    SELECT 'user_uuid', 'uuid', NULL
    UNION ALL
    SELECT 'token_hash', 'character varying', 64
    UNION ALL
    SELECT 'expires_at', 'timestamp with time zone', NULL
    UNION ALL
    SELECT 'used_at', 'timestamp with time zone', NULL
    UNION ALL
    SELECT 'created_at', 'timestamp with time zone', NULL
),
matched_columns AS (
    SELECT
        e.column_name,
        e.data_type,
        e.char_len,
        c.column_name AS found_column_name,
        c.data_type AS found_data_type,
        c.character_maximum_length AS found_char_len
    FROM expected_columns e
    LEFT JOIN information_schema.columns c
      ON c.table_schema = 'public'
     AND c.table_name = 'tb_password_reset'
     AND c.column_name = e.column_name
)
INSERT INTO verification_results (check_name, ok, details)
SELECT
    'TB_PASSWORD_RESET exists with correct fields',
    EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'tb_password_reset'
    )
    AND NOT EXISTS (
        SELECT 1
        FROM matched_columns
        WHERE found_column_name IS NULL
           OR found_data_type <> data_type
           OR COALESCE(found_char_len, -1) <> COALESCE(char_len, -1)
    ),
    CASE
        WHEN NOT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'tb_password_reset'
        ) THEN 'Missing table TB_PASSWORD_RESET'
        WHEN EXISTS (
            SELECT 1
            FROM matched_columns
            WHERE found_column_name IS NULL
               OR found_data_type <> data_type
               OR COALESCE(found_char_len, -1) <> COALESCE(char_len, -1)
        ) THEN 'TB_PASSWORD_RESET exists but fields do not match expected structure'
        ELSE 'OK'
    END;

INSERT INTO verification_results (check_name, ok, details)
SELECT
    'Append-only triggers active on TB_POLICY_VERSION and TB_POLICY_CLAUSE',
    (
        SELECT COUNT(*)
        FROM pg_trigger t
        JOIN pg_class c
          ON c.oid = t.tgrelid
        JOIN pg_namespace n
          ON n.oid = c.relnamespace
        JOIN pg_proc p
          ON p.oid = t.tgfoid
        WHERE n.nspname = 'public'
          AND c.relname IN ('tb_policy_version', 'tb_policy_clause')
          AND NOT t.tgisinternal
          AND p.proname = 'fn_protect_append_only'
    ) = 2,
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM pg_trigger t
            JOIN pg_class c
              ON c.oid = t.tgrelid
            JOIN pg_namespace n
              ON n.oid = c.relnamespace
            JOIN pg_proc p
              ON p.oid = t.tgfoid
            WHERE n.nspname = 'public'
              AND c.relname IN ('tb_policy_version', 'tb_policy_clause')
              AND NOT t.tgisinternal
              AND p.proname = 'fn_protect_append_only'
        ) = 2 THEN 'OK'
        ELSE 'Missing append-only protection trigger on TB_POLICY_VERSION and/or TB_POLICY_CLAUSE'
    END;

SELECT
    check_name,
    CASE WHEN ok THEN 'PASS' ELSE 'FAIL' END AS status,
    details
FROM verification_results
ORDER BY check_name;

DO $$
DECLARE
    failure_list TEXT;
BEGIN
    SELECT string_agg(check_name, '; ' ORDER BY check_name)
      INTO failure_list
      FROM verification_results
     WHERE ok = false;

    IF failure_list IS NOT NULL THEN
        RAISE EXCEPTION 'Database verification failed: %', failure_list;
    END IF;
END $$;

ROLLBACK;