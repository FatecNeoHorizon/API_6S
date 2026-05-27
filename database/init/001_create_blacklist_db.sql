SELECT 'CREATE DATABASE tecsys_blacklist'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'tecsys_blacklist')
\gexec

\connect tecsys_blacklist

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS blacklist (
    ID UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    USER_ID UUID NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS UX_blacklist_user_id
    ON blacklist (USER_ID);
