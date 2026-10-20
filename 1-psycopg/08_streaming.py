import psycopg as ps
from psycopg import sql
import time


def get_settings() -> dict[str, str]:
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


# Version 1: load data_2022_oct from the CSV with COPY (4 columns + id)

# import csv
#
#
# def main() -> None:
#
#     settings: dict = get_settings()
#
#     table = "data_2022_oct"
#
#     with ps.connect(**settings) as conn:
#
#         # Deleting
#         conn.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table)))
#
#         # Creating
#         conn.execute(sql.SQL("""
#                              CREATE TABLE IF NOT EXISTS {} (
#                                  id             serial PRIMARY KEY,
#                                  product_id     integer,
#                                  price          numeric(10, 2),
#                                  user_id        bigint,
#                                  user_session   uuid)""").format(sql.Identifier(table)))
#
#         with conn.cursor() as cur:
#             with cur.copy(
#                 sql.SQL(
#                     """
#                         COPY {} (product_id, price, user_id, user_session) FROM STDIN"""
#                 ).format(sql.Identifier(table))
#             ) as copy, open("../csv/customer/data_2022_oct.csv") as file:
#                 reader = csv.reader(file)
#                 next(reader)
#                 for row in reader:
#                     copy.write_row([value or None for value in row[2:]])
#
#     return None
#
#
# if __name__ == "__main__":
#     main()


# Version 2 (exercise): count by streaming vs SELECT COUNT(*)


def main() -> None:

    settings: dict = get_settings()

    with ps.connect(**settings) as conn:

        start = time.perf_counter()
        with conn.cursor(name="Reader") as src:
            src.execute("SELECT 1 FROM data_2022_oct")
            count = 0
            while rows := src.fetchmany(10_000):
                count += len(rows)

        print("streaming:", count, time.perf_counter() - start)

        start = time.perf_counter()
        count = conn.execute("SELECT COUNT(*) FROM data_2022_oct").fetchone()[0]
        print("COUNT(*):", count, time.perf_counter() - start)

    return None


if __name__ == "__main__":
    main()
