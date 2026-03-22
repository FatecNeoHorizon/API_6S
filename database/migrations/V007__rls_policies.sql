CREATE POLICY policy_select_user
ON TB_USER
FOR SELECT
USING (USER_UUID = current_setting('app.current_user_id')::UUID);

CREATE POLICY policy_update_user
ON TB_USER
FOR UPDATE
USING (USER_UUID = current_setting('app.current_user_id')::UUID);

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