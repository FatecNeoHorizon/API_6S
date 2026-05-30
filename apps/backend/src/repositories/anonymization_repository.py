from psycopg2.extensions import connection as PgConnection


def anonymize_user(conn: PgConnection, user_uuid: str) -> bool:
    """
    Anonymizes a user after mandatory consent revocation.

    USER_UUID is preserved as a technical non-identifying anchor so consent logs
    and foreign keys remain valid, while personal identifiers are replaced.
    """
    query = """
        UPDATE TB_USER
        SET USERNAME = CONCAT('anonymized_', REPLACE(USER_UUID::TEXT, '-', '')),
            EMAIL_HASH = CONCAT('anon_', REPLACE(USER_UUID::TEXT, '-', '')),
            EMAIL_ENC = '[removed]',
            PASSWORD_HASH = '[removed]',
            KEYCLOAK_SUB = NULL,
            ACTIVE = FALSE,
            FIRST_ACCESS_COMPLETED = FALSE,
            ANONYMIZED_AT = NOW(),
            DELETED_AT = NOW(),
            UPDATED_AT = NOW()
        WHERE USER_UUID = %s
          AND ANONYMIZED_AT IS NULL
          AND DELETED_AT IS NULL
        RETURNING USER_UUID
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (str(user_uuid),))
        row = cursor.fetchone()

    return row is not None