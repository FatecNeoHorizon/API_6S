CREATE OR REPLACE FUNCTION fn_current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_id', true), '')::UUID;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

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
        JOIN TB_PROFILE p
          ON p.PROFILE_UUID = u.PROFILE_ID
        WHERE u.USER_UUID = v_user_id
          AND p.PROFILE_NAME = 'ADMIN'
          AND u.ACTIVE = TRUE
          AND u.DELETED_AT IS NULL
    );
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = public;

CREATE POLICY policy_select_user
ON TB_USER
FOR SELECT
USING (USER_UUID = fn_current_user_id());

CREATE POLICY policy_update_user
ON TB_USER
FOR UPDATE
USING (USER_UUID = fn_current_user_id())
WITH CHECK (USER_UUID = fn_current_user_id());

CREATE POLICY policy_select_user_admin
ON TB_USER
FOR SELECT
USING (fn_current_user_is_admin());

CREATE POLICY policy_insert_user_admin
ON TB_USER
FOR INSERT
WITH CHECK (fn_current_user_is_admin());

CREATE POLICY policy_update_user_admin
ON TB_USER
FOR UPDATE
USING (fn_current_user_is_admin())
WITH CHECK (fn_current_user_is_admin());

CREATE POLICY policy_select_session_for_auth
ON TB_SESSION
FOR SELECT
USING (
    INVALIDATED_AT IS NULL
    AND EXPIRES_AT > NOW()
    AND DELETED_AT IS NULL
);

CREATE POLICY policy_select_session
ON TB_SESSION
FOR SELECT
USING (USER_ID = fn_current_user_id());

CREATE POLICY policy_insert_session
ON TB_SESSION
FOR INSERT
WITH CHECK (USER_ID = fn_current_user_id());

CREATE POLICY policy_update_session
ON TB_SESSION
FOR UPDATE
USING (USER_ID = fn_current_user_id())
WITH CHECK (USER_ID = fn_current_user_id());

CREATE POLICY policy_select_session_admin
ON TB_SESSION
FOR SELECT
USING (fn_current_user_is_admin());

CREATE POLICY policy_insert_session_admin
ON TB_SESSION
FOR INSERT
WITH CHECK (fn_current_user_is_admin());

CREATE POLICY policy_update_session_admin
ON TB_SESSION
FOR UPDATE
USING (fn_current_user_is_admin())
WITH CHECK (fn_current_user_is_admin());

CREATE POLICY policy_select_consent_log
ON TB_CONSENT_LOG
FOR SELECT
USING (USER_ID = fn_current_user_id());

CREATE POLICY policy_insert_consent_log
ON TB_CONSENT_LOG
FOR INSERT
WITH CHECK (USER_ID = fn_current_user_id());

ALTER TABLE TB_POLICY_VERSION ENABLE ROW LEVEL SECURITY;
ALTER TABLE TB_POLICY_CLAUSE ENABLE ROW LEVEL SECURITY;

CREATE POLICY policy_select_policy_version_public
ON TB_POLICY_VERSION
FOR SELECT
USING (
    DELETED_AT IS NULL
    AND EFFECTIVE_FROM <= NOW()
);

CREATE POLICY policy_select_policy_clause_public
ON TB_POLICY_CLAUSE
FOR SELECT
USING (
    DELETED_AT IS NULL
    AND EXISTS (
        SELECT 1
        FROM TB_POLICY_VERSION pv
        WHERE pv.VERSION_UUID = TB_POLICY_CLAUSE.POLICY_VERSION_ID
          AND pv.DELETED_AT IS NULL
          AND pv.EFFECTIVE_FROM <= NOW()
    )
);

CREATE POLICY policy_admin_policy_version
ON TB_POLICY_VERSION
FOR ALL
USING (fn_current_user_is_admin())
WITH CHECK (fn_current_user_is_admin());

CREATE POLICY policy_admin_policy_clause
ON TB_POLICY_CLAUSE
FOR ALL
USING (fn_current_user_is_admin())
WITH CHECK (fn_current_user_is_admin());

ALTER TABLE TB_USER FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_SESSION FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_CONSENT_LOG FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_POLICY_VERSION FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_POLICY_CLAUSE FORCE ROW LEVEL SECURITY;

CREATE UNIQUE INDEX IF NOT EXISTS UX_TB_SESSION_ONE_ACTIVE_PER_USER
    ON TB_SESSION (USER_ID)
    WHERE INVALIDATED_AT IS NULL;

CREATE INDEX IF NOT EXISTS IX_TB_SESSION_USER_ID_EXPIRES_AT
    ON TB_SESSION (USER_ID, EXPIRES_AT);

CREATE INDEX IF NOT EXISTS IX_TB_AUTH_ATTEMPT_EMAIL_HASH_ATTEMPTED_AT_DESC
    ON TB_AUTH_ATTEMPT (EMAIL_HASH, ATTEMPTED_AT DESC);

CREATE INDEX IF NOT EXISTS IX_TB_AUTH_ATTEMPT_SOURCE_IP_ATTEMPTED_AT_DESC
    ON TB_AUTH_ATTEMPT (SOURCE_IP, ATTEMPTED_AT DESC);