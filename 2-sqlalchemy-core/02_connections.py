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
                        id      serial PRIMARY KEY
                        name    text,
                        age     integer)"""))

    return None


def _insert(connection: sqlalchemy.Connection, name: str, age: int) -> None:

    connection.execute(
        sqlalchemy.text(
            """
                                       INSERT INTO practice_people (name, age) values (%s, %s)""".format(
                name, age
            )
        ),
    )


def main() -> None:

    engine = get_engine()

    with engine.connect() as connection:
        _create_table(connection)

        connection.commit()

    return None


if __name__ == "__main__":
    main()
