import sqlalchemy as sa
from pathlib import Path
from psycopg import sql, Connection
from typing import cast

# -------------------- connection ----------------------------------------


def get_password(file_path: Path) -> str:
    return file_path.read_text().strip()


def get_engine():
    url = sa.URL.create(
        "postgresql+psycopg",
        "hbourlot",
        get_password(Path(__file__).parent.parent / "db_password.txt"),
        "localhost",
        4242,
        "piscineds",
    )

    return sa.create_engine(url, echo=False)


# -------------------- end connection ------------------------------------


# -------------------- helpers -------------------------------------------


def _show_all_tables(engine: sa.Engine, metadata: sa.MetaData):

    metadata.reflect(engine)
    for name in metadata.tables:
        print(name)


# -------------------- end helpers ---------------------------------------


# -------------------- practice_people -----------------------------------


def _get_practice_people_table(metadata: sa.MetaData, table: str) -> sa.Table:

    people = sa.Table(
        table,
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("age", sa.Integer),
    )

    return people


def people_example(engine: sa.Engine, metadata: sa.MetaData) -> None:

    table: str = "practice_people"

    # Register
    people_table = _get_practice_people_table(metadata, table)

    metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(sa.text(f"TRUNCATE {table} RESTART IDENTITY"))
        conn.execute(people_table.insert().values(name="Hugo", age=29))
        conn.execute(people_table.insert().values(name="Sova", age=24))
        print(conn.execute(sa.text(f"SELECT * FROM {table}")).fetchall())

    # _show_all_tables(engine, metadata)


# -------------------- end practice_people -------------------------------


# -------------------- practice_events -----------------------------------


def _get_practice_events_table(metadata: sa.MetaData, table: str) -> sa.Table:

    events: sa.Table = sa.Table(
        table,
        metadata,
        sa.Column("event_time", sa.DateTime(timezone=True)),
        sa.Column("event_type", sa.Text),
        sa.Column("product_id", sa.Integer),
        sa.Column("price", sa.Numeric(10, 2)),
        sa.Column("user_id", sa.BigInteger),
        sa.Column("user_session", sa.Uuid),
    )

    return events


# -------------------- end practice_events -------------------------------


# -------------------- copy (load a CSV) ---------------------------------


def _copy_from_stdin(conn: sa.Connection, table: str, path: str) -> None:

    raw = cast(Connection, conn.connection.driver_connection)

    with raw.cursor() as cur:
        with cur.copy(
            sql.SQL("""
                              COPY {} FROM STDIN WITH (FORMAT csv, HEADER)""").format(
                sql.Identifier(table)
            )
        ) as copy:
            with open(path) as file:
                while data := file.read(1024 * 1024):
                    copy.write(data)
    return None


def _copy_from_file(conn: sa.Connection, table: str, path: str) -> None:

    conn.execute(sa.text(f"""
                         COPY {table}
                         FROM '{path}'
                         WITH (FORMAT csv, HEADER)"""))


# -------------------- end copy (load a CSV) -----------------------------


# -------------------- practice_events example ---------------------------


def events_example(engine: sa.Engine, metadata: sa.MetaData) -> None:

    table: str = "practice_events"

    events_table: sa.Table = _get_practice_events_table(metadata, table)

    metadata.create_all(engine)

    with engine.begin() as conn:
        # conn.execute(sa.text(f"TRUNCATE {table} RESTART IDENTITY"))
        # _copy_from_stdin(conn, table, "../csv/customer/data_2022_oct.csv")
        # _copy_from_file(conn, table, "/data/customer/data_2022_oct.csv")

        stmt = sa.select(events_table.c.price).where(events_table.c.price < 0)
        # print(stmt)

        # print(stmt.compile(compile_kwargs={"literal_binds": True}))

        # for (row,) in conn.execute(stmt):
        #     print(row)

        # cols = conn.execute(sa.text(f"SELECT * FROM {table}")).fetchmany(5)
        # for col in cols:
        #     print(*col)


# -------------------- end practice_events example -----------------------


# -------------------- main ----------------------------------------------


def main() -> None:

    engine: sa.Engine = get_engine()
    metadata = sa.MetaData()

    # people_example(engine, metadata)
    events_example(engine, metadata)

    return None


# -------------------- end main ------------------------------------------


if __name__ == "__main__":

    main()
