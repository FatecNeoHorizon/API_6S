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
SELECT '1.0.0', 'PRIVACY_POLICY', 'This privacy policy describes how users personal data is collected, stored, used and protected in accordance with Federal Law 13.709/2018 (General Data Protection Law - LGPD). The data collected is used exclusively for the purposes informed at the time of registration. The data subject has the right to access, correct, delete and revoke consent at any time. Data is stored in a secure environment with encryption at rest and in transit. This policy takes effect on the date of publication and may be updated with prior notice to the data subject.', NOW()
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0');

INSERT INTO TB_POLICY_CLAUSE (POLICY_VERSION_ID, CODE, TITLE, DESCRIPTION, MANDATORY, DISPLAY_ORDER)
SELECT
    (SELECT VERSION_UUID FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0' AND POLICY_TYPE = 'PRIVACY_POLICY'),
    'DATA_COLLECTION',
    'Consent for Data Collection',
    'The data subject must provide explicit consent for the collection and processing of their personal data, as provided by the LGPD.',
    true,
    1
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_CLAUSE WHERE CODE = 'DATA_COLLECTION');

INSERT INTO TB_POLICY_CLAUSE (POLICY_VERSION_ID, CODE, TITLE, DESCRIPTION, MANDATORY, DISPLAY_ORDER)
SELECT
    (SELECT VERSION_UUID FROM TB_POLICY_VERSION WHERE VERSION = '1.0.0' AND POLICY_TYPE = 'PRIVACY_POLICY'),
    'MARKETING',
    'Consent for Marketing Communications',
    'The data subject may optionally consent to receive promotional communications and marketing materials. This consent may be revoked at any time.',
    false,
    2
WHERE NOT EXISTS (SELECT 1 FROM TB_POLICY_CLAUSE WHERE CODE = 'MARKETING');