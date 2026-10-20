import psycopg
from psycopg import sql, Rollback


def get_settings() -> dict:

    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def insert_people(cur: psycopg.Cursor, name: str, age: int | str) -> None:
    cur.execute(
        "INSERT INTO practice_people (name, age) VALUES (%s, %s)",
        (
            name,
            age,
        ),
    )


def main() -> None:

    settings: dict = get_settings()

    with psycopg.connect(**settings, autocommit=True) as conn:
        cur = conn.cursor()

        try:
            # insert_people(cur, "ABC", "ABC")
            conn.execute(
                "INSERT INTO practice_people (name, age) VALUES (%s, %s)",
                ("jaaaa", 25),
            )
            # conn.commit()
            conn.execute(
                "INSERT INTO practice_people (name, age) VALUES (%s, %s)",
                ("j", "a"),
            )
        except psycopg.Error as e:
            print("Error -> ", e)
            conn.rollback()

        print(conn.execute("SELECT * FROM practice_people").fetchall())

    return None


if __name__ == "__main__":
    main()
