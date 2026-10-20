import psycopg


def get_password(path) -> str:

    return open(path).read().strip()


def get_settings() -> dict:

    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": get_password("../db_password.txt"),
        "host": "localhost",
        "port": "4242",
    }


def main() -> None:

    settings: dict = get_settings()

    with psycopg.connect(**settings) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM data_2022_oct LIMIT 5")
            print(cur.fetchone())
            print(cur.rowcount)

    return None


if __name__ == "__main__":
    main()
