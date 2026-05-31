-- Remove tables that are no longer needed now that Keycloak handles
-- first-access password setup and password reset flows.
DROP TABLE IF EXISTS TB_FIRST_ACCESS_TOKEN CASCADE;
DROP TABLE IF EXISTS TB_PASSWORD_RESET CASCADE;
