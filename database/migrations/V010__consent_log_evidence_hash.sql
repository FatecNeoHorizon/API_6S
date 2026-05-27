-- Adds a deterministic evidence hash to TB_CONSENT_LOG.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE TB_CONSENT_LOG
    ADD COLUMN IF NOT EXISTS CONSENT_HASH VARCHAR(64);

CREATE OR REPLACE FUNCTION fn_compute_consent_log_hash(
    p_user_id UUID,
    p_clause_id UUID,
    p_policy_version_id UUID,
    p_action VARCHAR,
    p_created_at TIMESTAMPTZ
)
RETURNS VARCHAR(64) AS $$
    SELECT encode(
        digest(
            concat_ws(
                '|',
                lower(p_user_id::TEXT),
                lower(p_clause_id::TEXT),
                lower(COALESCE(p_policy_version_id::TEXT, '')),
                upper(p_action),
                to_char(p_created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"')
            ),
            'sha256'
        ),
        'hex'
    );
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE FUNCTION fn_set_consent_log_hash()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CREATED_AT IS NULL THEN
        NEW.CREATED_AT := NOW();
    END IF;

    NEW.CONSENT_HASH := fn_compute_consent_log_hash(
        NEW.USER_ID,
        NEW.CLAUSE_ID,
        NEW.POLICY_VERSION_ID,
        NEW.ACTION,
        NEW.CREATED_AT
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS TB_CONSENT_LOG_SET_HASH ON TB_CONSENT_LOG;

CREATE TRIGGER TB_CONSENT_LOG_SET_HASH
    BEFORE INSERT ON TB_CONSENT_LOG
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_consent_log_hash();

-- Backfill existing rows. The append-only trigger must be bypassed here because
-- this UPDATE only adds a derived field and does not alter the semantic content of the record.
ALTER TABLE TB_CONSENT_LOG DISABLE TRIGGER TB_CONSENT_LOG_APPEND_ONLY;

UPDATE TB_CONSENT_LOG
SET CONSENT_HASH = fn_compute_consent_log_hash(
    USER_ID,
    CLAUSE_ID,
    POLICY_VERSION_ID,
    ACTION,
    CREATED_AT
)
WHERE CONSENT_HASH IS NULL;

ALTER TABLE TB_CONSENT_LOG ENABLE TRIGGER TB_CONSENT_LOG_APPEND_ONLY;

ALTER TABLE TB_CONSENT_LOG
    ALTER COLUMN CONSENT_HASH SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS UX_TB_CONSENT_LOG_CONSENT_HASH
    ON TB_CONSENT_LOG (CONSENT_HASH);