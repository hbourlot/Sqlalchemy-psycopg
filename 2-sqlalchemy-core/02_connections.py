import sqlalchemy
from pathlib import Path


def get_password(path: Path) -> str:
    return path.read_text().strip()


def get_engine() -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(
        sqlalchemy.URL.create(
            "postgresql+psycopg",
            "hbourlot",
            get_password(Path(__file__).parent.parent / "db_password.txt"),
            "localhost",
            4242,
            "piscineds",
        ),
        echo=False,
    )


def _create_table(connection: sqlalchemy.Connection) -> None:

    connection.execute(sqlalchemy.text("""
                        CREATE TABLE IF NOT EXISTS practice_people (
                        id      serial PRIMARY KEY,
                        name    text,
                        age     integer)"""))

    return None


def _truncate_table(conn: sqlalchemy.Connection, table: str) -> None:

    conn.execute(sqlalchemy.text(f"TRUNCATE {table} RESTART IDENTITY"))

    return None


def _insert_people(connection: sqlalchemy.Connection, name: str, age: int) -> None:

    connection.execute(
        sqlalchemy.text("""
                INSERT INTO practice_people (name, age) values (:name, :age)"""),
        {"name": name, "age": age},
    )


def _show_people(conn: sqlalchemy.Connection, table: str, limit: int) -> None:
    rows = conn.execute(
        sqlalchemy.text(f"SELECT * FROM {table} LIMIT :limit"),
        {"limit": limit},
    )

    for row in rows:
        print(row.name, row.age, row._mapping)

    return None


def _show_people_no_sql(conn: sqlalchemy.Connection, table: str, limit: int) -> None:

    t = sqlalchemy.table(table)
    rows = conn.execute(
        sqlalchemy.select(sqlalchemy.text("*")).select_from(t).limit(limit)
    )

    for row in rows:
        print(row.name, row.age, row._mapping)

    return None


def _show_people_examples(conn: sqlalchemy.Connection, table: str) -> None:

    query = sqlalchemy.text(f"SELECT * FROM {table}")
    print(conn.execute(query).scalar())

    # Return a _engine.ScalarResult filtering object which will return single elements rather than _row.Row objects.
    print(conn.execute(query).scalars().fetchall())

    print(conn.execute(query).fetchall())
    print(conn.execute(query).fetchone())

    return None


def _count(conn: sqlalchemy.Connection, table: str) -> int:

    return conn.execute(sqlalchemy.text(f"SELECT count(*) FROM {table}")).scalar_one()


def _without_begin(engine: sqlalchemy.Engine, table: str) -> None:
    """connect() without commit(): ROLLBACK at the end, the row is lost."""

    with engine.connect() as connection:
        _insert_people(connection, "Lost", 99)
        print("inside connect():", _count(connection, table))

    with engine.connect() as connection:
        print("after connect():", _count(connection, table))

    return None


def _with_begin(engine: sqlalchemy.Engine, table: str) -> None:
    """begin(): COMMIT at the end, the row is saved."""

    with engine.begin() as connection:
        _insert_people(connection, "Kept", 42)
        print("inside begin():", _count(connection, table))

    with engine.connect() as connection:
        print("after begin():", _count(connection, table))

    return None


def main() -> None:

    engine = get_engine()
    table: str = "practice_people"

    with engine.begin() as connection:
        _create_table(connection)
        _truncate_table(connection, table)

    _without_begin(engine, table)
    _with_begin(engine, table)

    return None


if __name__ == "__main__":
    main()
