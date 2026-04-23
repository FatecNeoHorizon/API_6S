CREATE POLICY policy_select_user
ON TB_USER
FOR SELECT
USING (USER_UUID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_update_user
ON TB_USER
FOR UPDATE
USING (USER_UUID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_select_user_admin
ON TB_USER
FOR SELECT
USING (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_insert_user_admin
ON TB_USER
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_update_user_admin
ON TB_USER
FOR UPDATE
USING (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_select_session
ON TB_SESSION
FOR SELECT
USING (USER_ID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_insert_session
ON TB_SESSION
FOR INSERT
WITH CHECK (USER_ID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_update_session
ON TB_SESSION
FOR UPDATE
USING (USER_ID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_select_session_admin
ON TB_SESSION
FOR SELECT
USING (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_insert_session_admin
ON TB_SESSION
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_update_session_admin
ON TB_SESSION
FOR UPDATE
USING (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
)
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM TB_USER auth_user
        JOIN TB_PROFILE auth_profile
          ON auth_profile.PROFILE_UUID = auth_user.PROFILE_ID
        WHERE auth_user.USER_UUID = current_setting('app.current_user_id')::UUID
          AND auth_profile.PROFILE_NAME = 'ADMIN'
    )
);

CREATE POLICY policy_select_consent_log
ON TB_CONSENT_LOG
FOR SELECT
USING (USER_ID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_insert_consent_log
ON TB_CONSENT_LOG
FOR INSERT
WITH CHECK (USER_ID = current_setting('app.current_user_id')::UUID);

ALTER TABLE TB_USER FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_SESSION FORCE ROW LEVEL SECURITY;
ALTER TABLE TB_CONSENT_LOG FORCE ROW LEVEL SECURITY;

CREATE UNIQUE INDEX IF NOT EXISTS UX_TB_SESSION_ONE_ACTIVE_PER_USER
    ON TB_SESSION (USER_ID)
    WHERE INVALIDATED_AT IS NULL;

CREATE INDEX IF NOT EXISTS IX_TB_SESSION_USER_ID_EXPIRES_AT
    ON TB_SESSION (USER_ID, EXPIRES_AT);

CREATE INDEX IF NOT EXISTS IX_TB_AUTH_ATTEMPT_EMAIL_HASH_ATTEMPTED_AT_DESC
    ON TB_AUTH_ATTEMPT (EMAIL_HASH, ATTEMPTED_AT DESC);

CREATE INDEX IF NOT EXISTS IX_TB_AUTH_ATTEMPT_SOURCE_IP_ATTEMPTED_AT_DESC
    ON TB_AUTH_ATTEMPT (SOURCE_IP, ATTEMPTED_AT DESC);