-- Remove Foreign Key constraints to allow physical deletion of users
-- Historical data will be preserved with orphaned USER_ID references

ALTER TABLE IF EXISTS tb_session DROP CONSTRAINT IF EXISTS tb_session_user_id_fkey;
ALTER TABLE IF EXISTS tb_password_reset DROP CONSTRAINT IF EXISTS tb_password_reset_user_uuid_fkey;
ALTER TABLE IF EXISTS tb_first_access_token DROP CONSTRAINT IF EXISTS tb_first_access_token_user_id_fkey;
ALTER TABLE IF EXISTS tb_consent_log DROP CONSTRAINT IF EXISTS tb_consent_log_user_id_fkey;
