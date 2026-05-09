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
                p.PROFILE_NAME
            FROM TB_SESSION s
            JOIN TB_USER u
              ON u.USER_UUID = s.USER_ID
            JOIN TB_PROFILE p
              ON p.PROFILE_UUID = u.PROFILE_ID
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