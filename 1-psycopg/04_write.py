import psycopg
from psycopg import sql


class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age


def get_settings() -> dict:
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": "mysecretpassword",
        "host": "localhost",
        "port": "4242",
    }


def create_table(conn: psycopg.Connection, name: str) -> None:
    conn.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                id          serial PRIMARY KEY,
                name        text,
                age         integer)
                """).format(sql.Identifier(name)))


def insert_into_table(conn: psycopg.Connection, table: str, person: Person) -> None:
    conn.execute(
        sql.SQL("""INSERT INTO {} (name, age) VALUES (%s, (%s))
                 """).format(sql.Identifier(table)),
        (person.name, person.age),
    )


def delete_table(conn: psycopg.Connection, table: str) -> None:
    conn.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table)))


def update_age_by_id(conn: psycopg.Connection, table, new_age: int, id: int) -> None:

    conn.execute(
        sql.SQL("UPDATE {} SET age = %s WHERE id = %s").format(sql.Identifier(table)),
        (new_age, 1),
    )


def update_age_by_name(
    conn: psycopg.Connection, table: str, new_age: int, name: str
) -> None:
    conn.execute(
        sql.SQL("UPDATE {} SET age = %s WHERE name = %s").format(sql.Identifier(table)),
        (new_age, name),
    )


def delete_by_id(conn: psycopg.Connection, table: str, id: int) -> None:
    conn.execute(
        sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(table)), (id,)
    )


def main() -> None:
    settings: dict = get_settings()

    table = "practice_people"
    first_person: Person = Person("Sova", 25)
    second_person: Person = Person("Hugo", 29)

    with psycopg.connect(**settings) as conn:
        # delete_table(conn, table)

        create_table(conn, table)

        # insert_into_table(conn, table, first_person)
        # insert_into_table(conn, table, second_person)

        update_age_by_name(conn, table, 25, "Hugo")
        delete_by_id(conn, table, 7)
        with conn.cursor() as cur:
            cur.execute(f"""SELECT * FROM {table}""")
            print(cur.fetchall())

    return None


if __name__ == "__main__":
    main()
