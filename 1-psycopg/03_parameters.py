import psycopg
from psycopg import sql


def get_settings() -> dict:
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def main() -> None:

    settings: dict = get_settings()

    table = "data_2022_oct"
    event_type = "'nothing OR '1'='1'"
    event_type = "purchase"

    with psycopg.connect(**settings) as conn:
        with conn.cursor() as cur:

            query = sql.SQL("SELECT count(*) FROM {} WHERE event_type = %s").format(
                sql.Identifier(table)
            )

            cur.execute(query, (event_type,))

            print(cur.fetchall())

    return None


if __name__ == "__main__":
    main()
