-- V014: Dev seed — admin test user linked to Keycloak
-- Keycloak sub matches the fixed UUID in keycloak/realm-zeus.json
-- EMAIL_ENC stores plain email for dev (EMAIL_ENCRYPTION_KEY not required in dev)

INSERT INTO TB_USER (USERNAME, EMAIL_ENC, KEYCLOAK_SUB, PROFILE_NAME, ACTIVE)
VALUES (
    'ADMIN',
    'admin@admin.com',
    'a1b2c3d4-0000-0000-0000-000000000001',
    'ADMIN',
    TRUE
)
ON CONFLICT (USERNAME) DO UPDATE
    SET KEYCLOAK_SUB = EXCLUDED.KEYCLOAK_SUB,
        PROFILE_NAME = EXCLUDED.PROFILE_NAME,
        ACTIVE       = EXCLUDED.ACTIVE;
