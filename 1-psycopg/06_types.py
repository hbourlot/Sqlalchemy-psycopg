import psycopg
from psycopg import sql
from psycopg.rows import dict_row, class_row, namedtuple_row
from datetime import datetime
from decimal import Decimal
from uuid import uuid4, UUID
from dataclasses import dataclass


@dataclass
class Item:
    id: int
    event_time: datetime
    event_type: str
    product_id: int
    price: Decimal
    user_id: int
    user_session: UUID


def get_settings() -> dict:

    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def _create_table(conn: psycopg.Connection, name: str) -> None:
    conn.execute(sql.SQL("""
                         CREATE TABLE IF NOT EXISTS {} (
                             id             serial PRIMARY KEY,
                             event_time     timestamptz,
                             event_type     text,
                             product_id     integer,
                             price          numeric(10, 2),
                             user_id        bigint,
                             user_session   uuid)""").format(sql.Identifier(name)))


def _load_table(conn: psycopg.Connection, table: str, path: str) -> None:
    conn.execute(sql.SQL("""
            COPY {} (event_time, event_type, product_id, price, user_id, user_session)
            FROM {}
            WITH (FORMAT csv, HEADER)
        """).format(sql.Identifier(table), sql.Literal(path)))


def _load_table_from_stdin(conn: psycopg.Connection, table: str, path: str) -> None:
    query = sql.SQL("""
                         COPY {} (event_time, event_type, product_id, price, user_id, user_session)
                         FROM STDIN WITH (FORMAT csv, HEADER)""").format(
        sql.Identifier(table)
    )

    with conn.cursor() as cur, cur.copy(query) as copy, open(path) as f:
        for line in f:
            copy.write(line)


# Version 1: create practice_events and load October into it

# def main() -> None:
#
#     settings: dict = get_settings()
#
#     with psycopg.connect(**settings) as conn:
#
#         try:
#             with conn.transaction():
#                 _create_table(conn, "practice_events")
#                 # server side: Postgres reads the file inside Docker
#                 _load_table(conn, "practice_events", "/data/customer/data_2022_oct.csv")
#                 # or client side: Python sends the file from the Mac
#                 # _load_table_from_stdin(
#                 #     conn, "practice_events", "../csv/customer/data_2022_oct.csv"
#                 # )
#
#         except psycopg.Error as e:
#             print("Error: ", e)
#             conn.rollback()
#
#     return None
#
#
# if __name__ == "__main__":
#     main()


# Version 2 (exercise): read rows of practice_events as dicts, print each value's type

def main() -> None:

    settings: dict = get_settings()

    with psycopg.connect(**settings) as conn:

        try:
            with conn.transaction():
                cur = conn.cursor(row_factory=dict_row)
                rows = cur.execute("SELECT * FROM practice_events").fetchmany(5)

                for row in rows:
                    for column, value in row.items():
                        print(column, type(value).__name__, value)
                    print()

        except psycopg.Error as e:
            print("Error: ", e)
            conn.rollback()

    return None


if __name__ == "__main__":
    main()
