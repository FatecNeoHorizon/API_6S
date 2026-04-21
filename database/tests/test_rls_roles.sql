\set ON_ERROR_STOP on

BEGIN;

\echo 'TEST 1: dba_role bypasses RLS on TB_USER and TB_SESSION'
SET ROLE dba_role;

DO $$
DECLARE
    v_user_count INTEGER;
    v_session_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_user_count FROM TB_USER;
    SELECT COUNT(*) INTO v_session_count FROM TB_SESSION;

    IF v_user_count < 2 THEN
        RAISE EXCEPTION 'FAIL: dba_role should see all users, got %', v_user_count;
    END IF;

    IF v_session_count < 2 THEN
        RAISE EXCEPTION 'FAIL: dba_role should see all sessions, got %', v_session_count;
    END IF;
END $$;

RESET ROLE;

\echo 'TEST 2: app_role with non-admin user stays restricted'
SET ROLE app_role;
SELECT set_config(
    'app.current_user_id',
    (SELECT USER_UUID::TEXT FROM TB_USER WHERE USERNAME = 'analyst_active'),
    false
);

DO $$
DECLARE
    v_user_count INTEGER;
    v_session_count INTEGER;
    v_updated_rows INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_user_count FROM TB_USER;
    SELECT COUNT(*) INTO v_session_count FROM TB_SESSION;

    UPDATE TB_USER
       SET ACTIVE = ACTIVE
     WHERE USERNAME = 'admin_active';

    GET DIAGNOSTICS v_updated_rows = ROW_COUNT;

    IF v_user_count <> 1 THEN
        RAISE EXCEPTION 'FAIL: analyst should see only own user row, got %', v_user_count;
    END IF;

    IF v_session_count <> 1 THEN
        RAISE EXCEPTION 'FAIL: analyst should see only own session row, got %', v_session_count;
    END IF;

    IF v_updated_rows <> 0 THEN
        RAISE EXCEPTION 'FAIL: analyst should not update another user, updated % rows', v_updated_rows;
    END IF;
END $$;

RESET ROLE;
RESET app.current_user_id;

\echo 'TEST 3: app_role with ADMIN profile can view and update any user/session'
SET ROLE app_role;
SELECT set_config(
    'app.current_user_id',
    (SELECT USER_UUID::TEXT FROM TB_USER WHERE USERNAME = 'admin_active'),
    false
);

DO $$
DECLARE
    v_user_count INTEGER;
    v_session_count INTEGER;
    v_updated_user_rows INTEGER;
    v_updated_session_rows INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_user_count FROM TB_USER;
    SELECT COUNT(*) INTO v_session_count FROM TB_SESSION;

    UPDATE TB_USER
       SET ACTIVE = ACTIVE
     WHERE USERNAME = 'manager_active';

    GET DIAGNOSTICS v_updated_user_rows = ROW_COUNT;

    UPDATE TB_SESSION
       SET INVALIDATED_AT = INVALIDATED_AT
     WHERE USER_ID = (SELECT USER_UUID FROM TB_USER WHERE USERNAME = 'analyst_active');

    GET DIAGNOSTICS v_updated_session_rows = ROW_COUNT;

    IF v_user_count < 3 THEN
        RAISE EXCEPTION 'FAIL: admin should see all user rows, got %', v_user_count;
    END IF;

    IF v_session_count < 3 THEN
        RAISE EXCEPTION 'FAIL: admin should see all session rows, got %', v_session_count;
    END IF;

    IF v_updated_user_rows <> 1 THEN
        RAISE EXCEPTION 'FAIL: admin should update another user, updated % rows', v_updated_user_rows;
    END IF;

    IF v_updated_session_rows <> 1 THEN
        RAISE EXCEPTION 'FAIL: admin should update another user session, updated % rows', v_updated_session_rows;
    END IF;
END $$;

\echo 'TEST 4: app_role with ADMIN profile can insert user and session'
INSERT INTO TB_USER (
    USERNAME,
    EMAIL_HASH,
    EMAIL_ENC,
    PASSWORD_HASH,
    ACTIVE,
    PROFILE_ID
)
VALUES (
    'admin_policy_test_user',
    '9f2a4c6d8e1b3f50728496a0b1c2d3e4f5a6b7c8d9e0f112233445566778899a',
    'ENCRYPTED::admin.policy.test@example.com',
    '$2b$12$AdminPolicyInsertTestHashValue123456789012345678901234',
    TRUE,
    (SELECT PROFILE_UUID FROM TB_PROFILE WHERE PROFILE_NAME = 'ANALYST')
);

INSERT INTO TB_SESSION (
    USER_ID,
    SOURCE_IP,
    USER_AGENT,
    EXPIRES_AT,
    INVALIDATED_AT
)
VALUES (
    (SELECT USER_UUID FROM TB_USER WHERE USERNAME = 'admin_policy_test_user'),
    '10.10.10.10',
    'psql-test',
    NOW() + INTERVAL '1 day',
    NULL
);

DO $$
DECLARE
    v_inserted_user_count INTEGER;
    v_inserted_session_count INTEGER;
BEGIN
    SELECT COUNT(*)
      INTO v_inserted_user_count
      FROM TB_USER
     WHERE USERNAME = 'admin_policy_test_user';

    SELECT COUNT(*)
      INTO v_inserted_session_count
      FROM TB_SESSION
     WHERE USER_ID = (SELECT USER_UUID FROM TB_USER WHERE USERNAME = 'admin_policy_test_user');

    IF v_inserted_user_count <> 1 THEN
        RAISE EXCEPTION 'FAIL: admin insert user test failed';
    END IF;

    IF v_inserted_session_count <> 1 THEN
        RAISE EXCEPTION 'FAIL: admin insert session test failed';
    END IF;
END $$;

RESET ROLE;
RESET app.current_user_id;


\echo 'TEST 5: log_role can still insert into TB_CONSENT_LOG'
SET ROLE log_role;

INSERT INTO TB_CONSENT_LOG (
    USER_ID,
    CLAUSE_ID,
    ACTION,
    SOURCE_IP,
    CHANNEL
)
VALUES (
    (SELECT USER_UUID FROM TB_USER WHERE USERNAME = 'admin_active'),
    (SELECT CLAUSE_UUID FROM TB_POLICY_CLAUSE WHERE CODE = 'DATA_COLLECTION'),
    'CONSENT',
    '127.0.0.1',
    'psql-test'
);

RESET ROLE;

ROLLBACK;

\echo 'ALL TESTS PASSED'