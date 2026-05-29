-- V013: Move identity to Keycloak
--
-- Keycloak becomes the source of truth for username, email, password and roles.
-- TB_USER is slimmed to a LGPD anchor: keeps USER_UUID (PK/FK for audit tables),
-- KEYCLOAK_SUB (link to Keycloak), PROFILE_NAME (denormalised for RLS speed),
-- EMAIL_ENC (LGPD Art.18 portability export), and lifecycle columns.
--
-- Columns removed:
--   EMAIL_HASH  — uniqueness now enforced by Keycloak
--   PASSWORD_HASH — credentials managed exclusively by Keycloak
--   PROFILE_ID  — replaced by PROFILE_NAME VARCHAR (no FK, Keycloak is authoritative)

-- 1. Add PROFILE_NAME, populated from the current PROFILE_ID → TB_PROFILE join
ALTER TABLE TB_USER
    ADD COLUMN IF NOT EXISTS PROFILE_NAME VARCHAR(50);

UPDATE TB_USER u
   SET PROFILE_NAME = p.PROFILE_NAME
  FROM TB_PROFILE p
 WHERE p.PROFILE_UUID = u.PROFILE_ID;

ALTER TABLE TB_USER
    ALTER COLUMN PROFILE_NAME SET NOT NULL;

-- 2. Drop columns that move to Keycloak
ALTER TABLE TB_USER
    DROP CONSTRAINT IF EXISTS tb_user_profile_id_fkey,
    DROP COLUMN IF EXISTS EMAIL_HASH,
    DROP COLUMN IF EXISTS PASSWORD_HASH,
    DROP COLUMN IF EXISTS PROFILE_ID;

-- 3. Update fn_current_user_is_admin to use PROFILE_NAME directly (no TB_PROFILE join)
CREATE OR REPLACE FUNCTION fn_current_user_is_admin()
RETURNS BOOLEAN AS $$
DECLARE
    v_user_id UUID;
BEGIN
    v_user_id := fn_current_user_id();
    IF v_user_id IS NULL THEN
        RETURN FALSE;
    END IF;
    RETURN EXISTS (
        SELECT 1
        FROM TB_USER u
        WHERE u.USER_UUID = v_user_id
          AND u.PROFILE_NAME = 'ADMIN'
          AND u.ACTIVE = TRUE
          AND u.DELETED_AT IS NULL
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public;
