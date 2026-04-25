from src.database.postgres import dict_cursor


def list_current_terms(conn) -> list[dict]:
    """
    Lists all currently effective policy versions and their clauses.

    Rules required by issue #181:
    - EFFECTIVE_FROM <= NOW()
    - DELETED_AT IS NULL
    - clauses ordered by DISPLAY_ORDER
    - public endpoint, so no user filter is applied here
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT
                pv.VERSION_UUID,
                pv.VERSION,
                pv.POLICY_TYPE,
                pv.CONTENT,
                pv.EFFECTIVE_FROM,
                c.CLAUSE_UUID,
                c.CODE,
                c.TITLE,
                c.DESCRIPTION,
                c.MANDATORY,
                c.DISPLAY_ORDER
            FROM TB_POLICY_VERSION pv
            LEFT JOIN TB_POLICY_CLAUSE c
              ON c.POLICY_VERSION_ID = pv.VERSION_UUID
             AND c.DELETED_AT IS NULL
            WHERE pv.DELETED_AT IS NULL
              AND pv.EFFECTIVE_FROM <= NOW()
            ORDER BY
                pv.POLICY_TYPE,
                pv.EFFECTIVE_FROM DESC,
                c.DISPLAY_ORDER ASC
            """
        )

        return cur.fetchall()