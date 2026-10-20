import psycopg
from pathlib import Path


def get_password(path: str) -> str:
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
        print(conn.execute("SELECT version()").fetchone())

    return None


if __name__ == "__main__":

    main()
