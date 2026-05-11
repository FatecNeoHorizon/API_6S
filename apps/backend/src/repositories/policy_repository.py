from src.database.postgres import dict_cursor


def list_current_terms(conn) -> list[dict]:
    """
    Lists all currently effective policy versions and their clauses.
    """
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            WITH current_versions AS (
                SELECT
                    pv.VERSION_UUID,
                    pv.VERSION,
                    pv.POLICY_TYPE,
                    pv.CONTENT,
                    pv.EFFECTIVE_FROM,
                    ROW_NUMBER() OVER (
                        PARTITION BY pv.POLICY_TYPE
                        ORDER BY pv.EFFECTIVE_FROM DESC, pv.CREATED_AT DESC
                    ) AS rn
                FROM TB_POLICY_VERSION pv
                WHERE pv.DELETED_AT IS NULL
                  AND pv.EFFECTIVE_FROM <= NOW()
            )
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
                        FROM current_versions pv
            LEFT JOIN TB_POLICY_CLAUSE c
              ON c.POLICY_VERSION_ID = pv.VERSION_UUID
             AND c.DELETED_AT IS NULL
                        WHERE pv.rn = 1
            ORDER BY
                pv.POLICY_TYPE,
                pv.EFFECTIVE_FROM DESC,
                c.DISPLAY_ORDER ASC
            """
        )

        return cur.fetchall()


def policy_version_exists(conn, version: str, policy_type: str) -> bool:
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT 1
            FROM TB_POLICY_VERSION
            WHERE VERSION = %s
              AND POLICY_TYPE = %s
              AND DELETED_AT IS NULL
            LIMIT 1
            """,
            (version, policy_type),
        )

        return cur.fetchone() is not None


def create_policy_version(
    conn,
    version: str,
    policy_type: str,
    content: str,
    effective_from,
    description: str | None,
):
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO TB_POLICY_VERSION (
                VERSION,
                POLICY_TYPE,
                CONTENT,
                DESCRIPTION,
                EFFECTIVE_FROM
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
                VERSION_UUID,
                VERSION,
                POLICY_TYPE,
                CONTENT,
                DESCRIPTION,
                EFFECTIVE_FROM,
                CREATED_AT
            """,
            (version, policy_type, content, description, effective_from),
        )

        return cur.fetchone()


def list_policy_versions(conn) -> list[dict]:
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            WITH versions_with_counts AS (
                SELECT
                    pv.VERSION_UUID,
                    pv.VERSION,
                    pv.POLICY_TYPE,
                    pv.CONTENT,
                    pv.DESCRIPTION,
                    pv.EFFECTIVE_FROM,
                    pv.CREATED_AT,
                    COUNT(c.CLAUSE_UUID) AS CLAUSE_COUNT
                FROM TB_POLICY_VERSION pv
                LEFT JOIN TB_POLICY_CLAUSE c
                  ON c.POLICY_VERSION_ID = pv.VERSION_UUID
                 AND c.DELETED_AT IS NULL
                WHERE pv.DELETED_AT IS NULL
                GROUP BY
                    pv.VERSION_UUID,
                    pv.VERSION,
                    pv.POLICY_TYPE,
                    pv.CONTENT,
                    pv.DESCRIPTION,
                    pv.EFFECTIVE_FROM,
                    pv.CREATED_AT
            ),
            current_versions AS (
                SELECT VERSION_UUID
                FROM (
                    SELECT
                        VERSION_UUID,
                        POLICY_TYPE,
                        ROW_NUMBER() OVER (
                            PARTITION BY POLICY_TYPE
                            ORDER BY EFFECTIVE_FROM DESC, CREATED_AT DESC
                        ) AS rn
                    FROM versions_with_counts
                    WHERE EFFECTIVE_FROM <= NOW()
                ) ranked
                WHERE rn = 1
            )
            SELECT
                v.VERSION_UUID,
                v.VERSION,
                v.POLICY_TYPE,
                v.CONTENT,
                v.DESCRIPTION,
                v.EFFECTIVE_FROM,
                v.CREATED_AT,
                v.CLAUSE_COUNT,
                CASE
                    WHEN v.EFFECTIVE_FROM > NOW() THEN 'scheduled'
                    WHEN cv.VERSION_UUID IS NOT NULL THEN 'current'
                    ELSE 'expired'
                END AS STATUS
            FROM versions_with_counts v
            LEFT JOIN current_versions cv
              ON cv.VERSION_UUID = v.VERSION_UUID
            ORDER BY v.EFFECTIVE_FROM DESC, v.CREATED_AT DESC
            """
        )

        return cur.fetchall()


def get_policy_version(conn, version_id: str) -> dict | None:
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            WITH all_versions AS (
                SELECT
                    VERSION_UUID,
                    VERSION,
                    POLICY_TYPE,
                    CONTENT,
                    DESCRIPTION,
                    EFFECTIVE_FROM,
                    CREATED_AT
                FROM TB_POLICY_VERSION
                WHERE DELETED_AT IS NULL
            ),
            current_versions AS (
                SELECT VERSION_UUID
                FROM (
                    SELECT
                        VERSION_UUID,
                        POLICY_TYPE,
                        ROW_NUMBER() OVER (
                            PARTITION BY POLICY_TYPE
                            ORDER BY EFFECTIVE_FROM DESC, CREATED_AT DESC
                        ) AS rn
                    FROM all_versions
                    WHERE EFFECTIVE_FROM <= NOW()
                ) ranked
                WHERE rn = 1
            )
            SELECT
                v.VERSION_UUID,
                v.VERSION,
                v.POLICY_TYPE,
                v.CONTENT,
                v.DESCRIPTION,
                v.EFFECTIVE_FROM,
                v.CREATED_AT,
                CASE
                    WHEN v.EFFECTIVE_FROM > NOW() THEN 'scheduled'
                    WHEN cv.VERSION_UUID IS NOT NULL THEN 'current'
                    ELSE 'expired'
                END AS STATUS
            FROM all_versions v
            LEFT JOIN current_versions cv
              ON cv.VERSION_UUID = v.VERSION_UUID
            WHERE v.VERSION_UUID = %s
            """,
            (version_id,),
        )

        return cur.fetchone()


def clause_code_exists(conn, version_id: str, code: str) -> bool:
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT 1
            FROM TB_POLICY_CLAUSE
            WHERE POLICY_VERSION_ID = %s
              AND CODE = %s
              AND DELETED_AT IS NULL
            LIMIT 1
            """,
            (version_id, code),
        )

        return cur.fetchone() is not None


def create_clause(
    conn,
    version_id: str,
    code: str,
    title: str,
    description: str | None,
    mandatory: bool,
    display_order: int,
):
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            INSERT INTO TB_POLICY_CLAUSE (
                POLICY_VERSION_ID,
                CODE,
                TITLE,
                DESCRIPTION,
                MANDATORY,
                DISPLAY_ORDER
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING
                CLAUSE_UUID,
                POLICY_VERSION_ID,
                CODE,
                TITLE,
                DESCRIPTION,
                MANDATORY,
                DISPLAY_ORDER,
                CREATED_AT
            """,
            (version_id, code, title, description, mandatory, display_order),
        )

        return cur.fetchone()


def list_clauses(conn, version_id: str) -> list[dict]:
    with dict_cursor(conn) as cur:
        cur.execute(
            """
            SELECT
                CLAUSE_UUID,
                POLICY_VERSION_ID,
                CODE,
                TITLE,
                DESCRIPTION,
                MANDATORY,
                DISPLAY_ORDER,
                CREATED_AT
            FROM TB_POLICY_CLAUSE
            WHERE POLICY_VERSION_ID = %s
              AND DELETED_AT IS NULL
            ORDER BY DISPLAY_ORDER ASC
            """,
            (version_id,),
        )

        return cur.fetchall()