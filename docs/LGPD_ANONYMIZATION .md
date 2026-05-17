# LGPD ANONYMIZATION, LOGICAL EXCLUSION AND DATA RETENTION

## ANONYMIZATION & LOGICAL EXCLUSION
For anonymization and logical exclusion, we need only to alter/delete tables that contains the user id as a FK.
For the TB_CONSENT_LOG table, we keep the user id column but remove its reference to TB_USER
For other tables such as TB_PASSWORD_RESET, validate if they are indeed required and being used, if not we can safely drop those tables. Otherwise we just remove the user id reference to its TB_USER table

That way we ensure there is no referencial integrity to keep between the tables while also recording the user id on these tables.

Next we only need to change the 'delete users' feature to fully delete its equivalent row on TB_USER

## DATA RETENTION
To ensure data retention, we need to perform the following steps:

- Create a new database (ie USER_RETENTION_DB)
- On the created database, create a new table (ie DELETED_USERS) with two columns, one being an UUID serving as a PK, and another one is the id of the deleted user that was stored in TB_USER
- Change the 'delete users' feature so before it deletes anything, it creates a new row on DELETED_USERS with the id of the user being deleted
- Create a python function that calls pg_dump.exe via shell to dump the database containing TB_USERS
- Create a python function that modifies the .sql file created by pg_dump.exe, removing the insertion of users inside the DELETED_USERS table
- Create a python function that calls og_restore.exe via shell to restore the database using the modified .sql file

References:
- https://www.geeksforgeeks.org/postgresql/how-to-dump-and-restore-postgresql-database/
- https://www.geeksforgeeks.org/postgresql/postgresql-restore-database/