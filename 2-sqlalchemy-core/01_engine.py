import sqlalchemy as sa
from pathlib import Path


def get_password(path: Path) -> str:
    return path.read_text().strip()


def get_engine() -> sa.Engine:
    url = sa.URL.create(
        "postgresql+psycopg",
        "hbourlot",
        get_password(Path(__file__).parent.parent / "db_password.txt"),
        "localhost",
        4242,
        "piscineds",
    )

    return sa.create_engine(url, echo=True)


def main() -> None:

    engine = get_engine()

    with engine.connect() as conn:
        print(conn.execute(sa.text("SELECT version()")).scalar())
        print(conn.execute(sa.text("SELECT current_database()")).scalar())
        print(conn.execute(sa.text("SELECT current_user")).scalar())

    return None


if __name__ == "__main__":
    main()
