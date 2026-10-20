import psycopg as pg
from psycopg import sql
from psycopg_pool import ConnectionPool


def get_settings() -> dict[str, str]:
    """Return the PostgreSQL connection settings.

    Returns:
        dict[str, str]: Keyword arguments for psycopg.connect().
    """
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def _drop_table(cur: pg.Cursor, table: str) -> None:
    """Drop a table if it exists, safely quoting its name.

    Args:
        cur (pg.Cursor): Open cursor to execute on.
        table (str): Name of the table to drop.
    """

    cur.execute(sql.SQL("""
                        DROP TABLE IF EXISTS {}""").format(sql.Identifier(table)))

    return None


def _list_all_tables(cur: pg.Cursor) -> None:
    """Print every table name in the public schema, sorted.

    Args:
        cur (pg.Cursor): Open cursor to execute on.
    """

    cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY table_name""")

    for (table,) in cur:
        print(table)

    return None


def _uniqueViolation(settings: dict) -> None:
    """Demo UniqueViolation by inserting a duplicate primary key.

    Args:
        settings (dict): Connection settings for psycopg.connect().
    """

    with pg.connect(**settings) as conn:
        cur = conn.cursor()
        cur.execute("CREATE TEMP TABLE t (id int PRIMARY KEY)")
        cur.execute("INSERT INTO t VALUES (1)")

        try:
            cur.execute("INSERT INTO t VALUES (1)")

        except pg.errors.UniqueViolation as e:
            print(f"Error(UniqueViolation) : {e.diag.message_primary}")
            conn.rollback()


def _undefinedTable(settings: dict) -> None:
    """Demo UndefinedTable by inserting into a nonexistent table.

    Args:
        settings (dict): Connection settings for psycopg.connect().
    """

    with pg.connect(**settings) as conn:
        cur = conn.cursor()
        cur.execute("CREATE TEMP TABLE t (id int PRIMARY KEY)")
        cur.execute("INSERT INTO t VALUES (1)")

        try:
            cur.execute("INSERT INTO wrongName VALUES (1)")

        except pg.errors.UndefinedTable as e:
            print(f"Error(UndefinedTable) : {e.diag.message_primary}")
            conn.rollback()


def _inFailedSqlTransaction(settings: dict) -> None:
    """Demo InFailedSqlTransaction: after an error, every query fails until rollback.

    Also shows that rollback discards the temp table created in the same transaction.

    Args:
        settings (dict): Connection settings for psycopg.connect().
    """
    with pg.connect(**settings) as conn:
        cur = conn.cursor()
        cur.execute("CREATE TEMP TABLE t (id int PRIMARY KEY)")
        cur.execute("INSERT INTO t VALUES (1)")

        try:
            cur.execute("INSERT INTO wrongName VALUES (1)")

        except pg.errors.UndefinedTable as e:
            print(f"Error(UndefinedTable) : {e.diag.message_primary}")

            try:
                cur.execute("SELECT 1")
            except pg.errors.InFailedSqlTransaction as e:
                print(f"StuckError(inFailedSqlTransaction) : {e.diag.message_primary}")

            conn.rollback()

        cur.execute("SELECT to_regclass('pg_temp.t')")
        print("AFTER rollback, t =", cur.fetchone()[0])


def _operationalError(settings: dict) -> None:
    """Demo OperationalError by connecting to a port with no server.

    Args:
        settings (dict): Connection settings; the port is overridden.
    """
    try:
        with pg.connect(**{**settings, "port": "4229"}, connect_timeout=3) as conn:
            conn.execute("SELECT 1")
    except pg.OperationalError as e:
        print(f"Error(OperationalError) : {e}")


def _pool(settings: dict) -> None:
    """Open a ConnectionPool and run a query on a borrowed connection.

    Args:
        settings (dict): Connection settings passed to each pooled connection.
    """

    with ConnectionPool(conninfo="", kwargs=settings, min_size=1, max_size=4) as pool:
        with pool.connection() as conn:
            conn.execute("SELECT 1")


def main() -> None:
    """Run the selected error demos."""

    settings: dict = get_settings()

    print("\n\n")
    # _inFailedSqlTransaction(settings)
    # print("\n\n")
    # _undefinedTable(settings)
    # print("\n\n")
    # _uniqueViolation(settings)
    # print("\n\n")
    # _operationalError(settings)
    # print("\n\n")
    _pool(settings)


if __name__ == "__main__":
    main()
