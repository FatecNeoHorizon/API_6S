INSERT INTO TB_PROFILE (PROFILE_NAME, PERMISSIONS, DESCRIPTION)
SELECT 'ADMIN', '{"view": true, "edit": true, "insert": true, "delete": true, "admin": true}', 'Profile for system controllers with full operational administration.'
WHERE NOT EXISTS (SELECT 1 FROM TB_PROFILE WHERE PROFILE_NAME = 'ADMIN');

INSERT INTO TB_PROFILE (PROFILE_NAME, PERMISSIONS, DESCRIPTION)
SELECT 'ANALYST', '{"view": true, "edit": false, "insert": false, "delete": false, "admin": false}', 'Profile with read-only access for consultation and data visualization.'
WHERE NOT EXISTS (SELECT 1 FROM TB_PROFILE WHERE PROFILE_NAME = 'ANALYST');

INSERT INTO TB_PROFILE (PROFILE_NAME, PERMISSIONS, DESCRIPTION)
SELECT 'MANAGER', '{"view": true, "edit": true, "insert": false, "delete": false, "admin": false}', 'Profile with access to management features, without permission to change system rules.'
WHERE NOT EXISTS (SELECT 1 FROM TB_PROFILE WHERE PROFILE_NAME = 'MANAGER');

INSERT INTO TB_POLICY_VERSION (VERSION, POLICY_TYPE, CONTENT, EFFECTIVE_FROM)
SELECT '1.0.0', 'PRIVACY_POLICY', 'Esta política de privacidade descreve como os dados pessoais dos usuários são coletados, armazenados, utilizados e protegidos em conformidade com a Lei Federal nº 13.709/2018 (Lei Geral de Proteção de Dados - LGPD). Os dados coletados são utilizados exclusivamente para as finalidades informadas no momento do cadastro. O titular dos dados tem o direito de acessar, corrigir, excluir e revogar o consentimento a qualquer momento. Os dados são armazenados em ambiente seguro com criptografia em repouso e em trânsito. Esta política entra em vigor na data de sua publicação e poderá ser atualizada com aviso prévio ao titular dos dados.', NOW()
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0');

INSERT INTO TB_POLICY_CLAUSE (POLICY_VERSION_ID, CODE, TITLE, DESCRIPTION, MANDATORY, DISPLAY_ORDER)
SELECT
    (SELECT VERSION_UUID FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0' AND POLICY_TYPE = 'PRIVACY_POLICY'),
    'DATA_COLLECTION',
    'Consentimento para Coleta de Dados',
    'O titular deve fornecer consentimento explícito para a coleta e o tratamento de seus dados pessoais, conforme previsto pela LGPD.',
    true,
    1
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_CLAUSE WHERE CODE = 'DATA_COLLECTION');

INSERT INTO TB_POLICY_CLAUSE (POLICY_VERSION_ID, CODE, TITLE, DESCRIPTION, MANDATORY, DISPLAY_ORDER)
SELECT
    (SELECT VERSION_UUID FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0' AND POLICY_TYPE = 'PRIVACY_POLICY'),
    'MARKETING',
    'Consentimento para Comunicações de Marketing',
    'O titular pode, de forma opcional, consentir em receber comunicações promocionais e materiais de marketing. Este consentimento pode ser revogado a qualquer momento.',
    false,
    2
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_CLAUSE WHERE CODE = 'MARKETING');