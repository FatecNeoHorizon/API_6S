from src.database.postgres import dict_cursor


def get_session_user(conn, session_uuid: str) -> dict | None:
    """
    Reads the authenticated user from an active session.

    Repository layer rule:
    - only SQL;
    - no HTTPException;
    - no response formatting;
    - no business validation.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT
                s.SESSION_UUID,
                u.USER_UUID,
                u.PROFILE_NAME
            FROM TB_SESSION s
            JOIN TB_USER u
              ON u.USER_UUID = s.USER_ID
            WHERE s.SESSION_UUID = %s
              AND s.INVALIDATED_AT IS NULL
              AND s.EXPIRES_AT > NOW()
              AND s.DELETED_AT IS NULL
              AND u.ACTIVE = TRUE
              AND u.DELETED_AT IS NULL
            """,
            (session_uuid,),
        )

        return cur.fetchone()


def list_pending_clauses(conn, user_id: str) -> list[dict]:
    """
    Lists mandatory clauses pending consent for a specific authenticated user.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT
                CLAUSE_UUID,
                POLICY_VERSION_ID,
                POLICY_TYPE,
                VERSION,
                CLAUSE_CODE,
                CLAUSE_TITLE,
                CLAUSE_DESCRIPTION,
                MANDATORY,
                DISPLAY_ORDER
            FROM V_PENDING_CONSENT
            WHERE USER_UUID = %s
            ORDER BY POLICY_TYPE, VERSION, DISPLAY_ORDER
            """,
            (user_id,),
        )

        return cur.fetchall()


def list_user_consent_history(conn, user_id: str) -> list[dict]:
    """
    Lists immutable consent events for one authenticated user.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT
                cl.LOG_UUID,
                cl.ACTION,
                cl.CREATED_AT AS REGISTERED_AT,
                cl.SOURCE_IP,
                cl.USER_AGENT,
                cl.CHANNEL,
                cl.CONSENT_HASH,
                pv.VERSION_UUID AS POLICY_VERSION_ID,
                pv.POLICY_TYPE,
                pv.VERSION AS POLICY_VERSION,
                pc.CLAUSE_UUID,
                pc.CODE AS CLAUSE_CODE,
                pc.TITLE AS CLAUSE_TITLE,
                pc.MANDATORY
            FROM TB_CONSENT_LOG cl
            JOIN TB_POLICY_CLAUSE pc
              ON pc.CLAUSE_UUID = cl.CLAUSE_ID
            JOIN TB_POLICY_VERSION pv
              ON pv.VERSION_UUID = COALESCE(cl.POLICY_VERSION_ID, pc.POLICY_VERSION_ID)
            WHERE cl.USER_ID = %s
            ORDER BY cl.CREATED_AT DESC, cl.LOG_UUID DESC
            """,
            (user_id,),
        )

        return cur.fetchall()


def list_current_mandatory_clauses(conn) -> list[dict]:
    """
    Lists all mandatory clauses from currently effective policy versions.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
                        WITH current_versions AS (
                                SELECT
                                        pv.VERSION_UUID,
                                        pv.POLICY_TYPE,
                                        pv.VERSION,
                                        ROW_NUMBER() OVER (
                                                PARTITION BY pv.POLICY_TYPE
                                                ORDER BY pv.EFFECTIVE_FROM DESC, pv.CREATED_AT DESC
                                        ) AS rn
                                FROM TB_POLICY_VERSION pv
                                WHERE pv.DELETED_AT IS NULL
                                    AND pv.EFFECTIVE_FROM <= NOW()
                        )
            SELECT
                c.CLAUSE_UUID,
                c.POLICY_VERSION_ID,
                c.CODE,
                c.TITLE,
                pv.POLICY_TYPE,
                pv.VERSION
            FROM TB_POLICY_CLAUSE c
                        JOIN current_versions pv
                            ON pv.VERSION_UUID = c.POLICY_VERSION_ID
                        WHERE pv.rn = 1
              AND c.DELETED_AT IS NULL
              AND c.MANDATORY = TRUE
            ORDER BY pv.POLICY_TYPE, pv.VERSION, c.DISPLAY_ORDER
            """
        )

        return cur.fetchall()


def list_user_current_consent_preferences(conn, user_id: str) -> list[dict]:
    """
    Lists all current policy clauses and their latest consent state for one user.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            WITH current_versions AS (
                SELECT
                    pv.VERSION_UUID,
                    pv.VERSION,
                    pv.POLICY_TYPE,
                    ROW_NUMBER() OVER (
                        PARTITION BY pv.POLICY_TYPE
                        ORDER BY pv.EFFECTIVE_FROM DESC, pv.CREATED_AT DESC
                    ) AS rn
                FROM TB_POLICY_VERSION pv
                WHERE pv.DELETED_AT IS NULL
                  AND pv.EFFECTIVE_FROM <= NOW()
            )
            SELECT
                c.CLAUSE_UUID AS clause_uuid,
                c.POLICY_VERSION_ID AS policy_version_id,
                pv.POLICY_TYPE AS policy_type,
                pv.VERSION AS policy_version,
                c.CODE AS clause_code,
                c.TITLE AS clause_title,
                c.DESCRIPTION AS clause_description,
                c.MANDATORY AS mandatory,
                last_log.ACTION AS last_action,
                last_log.CREATED_AT AS last_action_at,
                CASE
                    WHEN last_log.ACTION IN ('CONSENT', 'CONSENT_ACCEPTED') THEN TRUE
                    ELSE FALSE
                END AS accepted,
                COALESCE(last_log.ACTION, 'PENDING') AS current_status
            FROM TB_POLICY_CLAUSE c
            JOIN current_versions pv
              ON pv.VERSION_UUID = c.POLICY_VERSION_ID
             AND pv.rn = 1
            LEFT JOIN LATERAL (
                SELECT
                    cl.ACTION,
                    cl.CREATED_AT
                FROM TB_CONSENT_LOG cl
                WHERE cl.USER_ID = %s
                  AND cl.CLAUSE_ID = c.CLAUSE_UUID
                ORDER BY cl.CREATED_AT DESC, cl.LOG_UUID DESC
                LIMIT 1
            ) last_log ON TRUE
            WHERE c.DELETED_AT IS NULL
            ORDER BY pv.POLICY_TYPE, pv.VERSION, c.DISPLAY_ORDER
            """,
            (user_id,),
        )

        return cur.fetchall()


def get_current_clause_for_consent_update(conn, clause_id: str) -> dict | None:
    """
    Resolves a clause from the current effective policy versions.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            WITH current_versions AS (
                SELECT
                    pv.VERSION_UUID,
                    pv.POLICY_TYPE,
                    pv.VERSION,
                    ROW_NUMBER() OVER (
                        PARTITION BY pv.POLICY_TYPE
                        ORDER BY pv.EFFECTIVE_FROM DESC, pv.CREATED_AT DESC
                    ) AS rn
                FROM TB_POLICY_VERSION pv
                WHERE pv.DELETED_AT IS NULL
                  AND pv.EFFECTIVE_FROM <= NOW()
            )
            SELECT
                c.CLAUSE_UUID AS clause_uuid,
                c.POLICY_VERSION_ID AS policy_version_id,
                c.MANDATORY AS mandatory,
                c.CODE AS code,
                c.TITLE AS title,
                pv.POLICY_TYPE AS policy_type,
                pv.VERSION AS version
            FROM TB_POLICY_CLAUSE c
            JOIN current_versions pv
              ON pv.VERSION_UUID = c.POLICY_VERSION_ID
             AND pv.rn = 1
            WHERE c.CLAUSE_UUID = %s
              AND c.DELETED_AT IS NULL
            LIMIT 1
            """,
            (clause_id,),
        )

        return cur.fetchone()


def insert_consent_event(
    conn,
    user_id: str,
    clause_uuid: str,
    policy_version_id: str,
    event_action: str,
    source_ip: str,
    user_agent: str,
) -> bool:
    """
    Inserts an immutable consent event.

    The service layer must already map:
    - CONSENT -> CONSENT_ACCEPTED
    - REVOCATION -> CONSENT_REVOKED
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO TB_CONSENT_LOG (
                USER_ID,
                CLAUSE_ID,
                POLICY_VERSION_ID,
                ACTION,
                SOURCE_IP,
                USER_AGENT,
                CHANNEL
            )
            SELECT
                %s,
                c.CLAUSE_UUID,
                c.POLICY_VERSION_ID,
                %s,
                %s,
                %s,
                'WEB'
            FROM TB_POLICY_CLAUSE c
            JOIN TB_POLICY_VERSION pv
              ON pv.VERSION_UUID = c.POLICY_VERSION_ID
            WHERE c.CLAUSE_UUID = %s
              AND c.POLICY_VERSION_ID = %s
              AND c.DELETED_AT IS NULL
              AND pv.DELETED_AT IS NULL
            RETURNING LOG_UUID
            """,
            (
                user_id,
                event_action,
                source_ip,
                user_agent[:512],
                clause_uuid,
                policy_version_id,
            ),
        )

        inserted = cur.fetchone()

    return inserted is not None