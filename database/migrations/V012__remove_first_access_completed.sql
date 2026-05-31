-- Remove column that is no longer needed now that Keycloak handles
-- the first-access (password setup) flow via requiredActions.
ALTER TABLE TB_USER DROP COLUMN IF EXISTS FIRST_ACCESS_COMPLETED;
