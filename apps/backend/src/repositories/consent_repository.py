from src.database.postgres import dict_cursor


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