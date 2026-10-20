import psycopg as ps
from psycopg import sql
import time


def get_settings() -> dict:
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def _create_table(conn: ps.Connection, name: str) -> None:
    conn.execute(sql.SQL("""
                         CREATE TABLE IF NOT EXISTS {} (
                             id             serial PRIMARY KEY,
                             event_time     timestamptz,
                             event_type     text,
                             product_id     integer,
                             price          numeric(10, 2),
                             user_id        bigint,
                             user_session   uuid)""").format(sql.Identifier(name)))


def _load_csv_from_stdin(cur: ps.Cursor, table: str, path: str) -> None:
    query = sql.SQL("""
                    COPY {} (event_time, event_type, product_id, price, user_id, user_session)
                    FROM STDIN WITH (FORMAT csv, HEADER)""").format(
        sql.Identifier(table)
    )

    with cur.copy(query) as copy, open(path) as f:
        while data := f.read(1024 * 1024):
            copy.write(data)


def _copy_rows(cur: ps.Cursor, table: str, rows: list[tuple]) -> None:
    query = sql.SQL(
        "COPY {} (event_type, product_id, price, user_session) FROM STDIN"
    ).format(sql.Identifier(table))

    with cur.copy(query) as copy:
        for row in rows:
            copy.write_row(row)


def _export_new_csv(cur: ps.Cursor, table: str) -> None:
    query = sql.SQL("""
            COPY (SELECT * FROM {}) TO STDOUT WITH (FORMAT csv, HEADER)""").format(
        sql.Identifier(table)
    )

    with open("out.csv", "wb") as f, cur.copy(query) as copy:
        for data in copy:
            f.write(data)


# Version 1: one COPY vs executemany on the same 10 000 rows

# def main() -> None:
#
#     settings: dict = get_settings()
#     table: str = "practice_copy"
#
#     with ps.connect(**settings) as conn:
#         cur = conn.cursor()
#
#         try:
#             with conn.transaction():
#                 rows = cur.execute(
#                     """SELECT event_type, product_id, price, user_session FROM practice_people LIMIT 10000"""
#                 ).fetchall()
#
#                 start = time.perf_counter()
#                 _copy_rows(cur, table, rows)
#                 print("copy:", time.perf_counter() - start)
#
#                 start = time.perf_counter()
#                 cur.executemany(
#                     "INSERT INTO practice_copy (event_type, product_id, price, user_session) VALUES (%s, %s, %s, %s)",
#                     rows,
#                 )
#                 print("executemany:", time.perf_counter() - start)
#
#         except ps.Error as e:
#             print("Error -> ", e)
#
#     return None
#
#
# if __name__ == "__main__":
#     main()


# Version 2 (exercise): load a CSV into a practice table, then export it to out.csv

def main() -> None:

    settings: dict = get_settings()
    table: str = "practice_copy"
    path: str = "../csv/customer/data_2022_oct.csv"

    with ps.connect(**settings) as conn:
        cur = conn.cursor()

        try:
            with conn.transaction():
                cur.execute(
                    sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table))
                )
                _create_table(conn, table)
                _load_csv_from_stdin(cur, table, path)
                _export_new_csv(cur, table)

        except ps.Error as e:
            print("Error -> ", e)

    return None


if __name__ == "__main__":
    main()
