import sqlalchemy as sa
from pathlib import Path

# -------------------- connection ----------------------------------------


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

    return sa.create_engine(url, echo=False)


# -------------------- end connection ------------------------------------


# -------------------- tables --------------------------------------------


def _get_practice_people_table(metadata: sa.MetaData, table: str) -> sa.Table:

    return sa.Table(
        table,
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.VARCHAR(100)),
        sa.Column("age", sa.Integer),
    )


def _get_practice_events_table(metadata: sa.MetaData, table: str) -> sa.Table:

    return sa.Table(
        table,
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("event_time", sa.DateTime(timezone=True)),
        sa.Column("event_type", sa.Text),
        sa.Column("product_id", sa.Integer),
        sa.Column("price", sa.Numeric(10, 2)),
        sa.Column("user_id", sa.BigInteger),
        sa.Column("user_session", sa.Uuid),
    )


# -------------------- end tables ----------------------------------------


# -------------------- helpers -------------------------------------------


def _exists(engine: sa.Engine, table: str) -> bool:

    return sa.inspect(engine).has_table(table)


def _db_columns(engine: sa.Engine, table: str) -> list[str]:
    """Columns as Postgres sees them, not as Python defines them."""

    return [col["name"] for col in sa.inspect(engine).get_columns(table)]


# -------------------- end helpers ---------------------------------------


# -------------------- 1. defining is not creating -----------------------


def define_is_not_create(engine: sa.Engine) -> None:

    metadata = sa.MetaData()
    _get_practice_people_table(metadata, "practice_ghost")

    # The Table lives only in Python (in metadata), Postgres knows nothing
    print("in metadata:", list(metadata.tables))
    print("in postgres:", _exists(engine, "practice_ghost"))

    return None


# -------------------- 2. create_all -------------------------------------


def create_all_example(engine: sa.Engine) -> None:

    metadata = sa.MetaData()
    _get_practice_people_table(metadata, "practice_people")
    _get_practice_events_table(metadata, "practice_events")

    # CREATE TABLE for every table in metadata, skips the ones that exist
    metadata.create_all(engine)
    print("people:", _exists(engine, "practice_people"))
    print("events:", _exists(engine, "practice_events"))

    # Second call does nothing (checkfirst=True by default), no error
    metadata.create_all(engine)

    return None


# -------------------- 3. drop_all and table.drop ------------------------


def drop_example(engine: sa.Engine) -> None:

    metadata = sa.MetaData()
    people = _get_practice_people_table(metadata, "practice_people")
    _get_practice_events_table(metadata, "practice_events")

    # Drop one table; checkfirst=True = no error if it is already gone
    people.drop(engine, checkfirst=True)
    people.drop(engine, checkfirst=True)
    print("people after drop:", _exists(engine, "practice_people"))

    # Drop every table in metadata (only the ones that exist)
    metadata.drop_all(engine)
    print("events after drop_all:", _exists(engine, "practice_events"))

    # Create both again
    metadata.create_all(engine)
    print("after create_all:", _exists(engine, "practice_people"))

    return None


# -------------------- 4. changing a Column later ------------------------


def change_column_later(engine: sa.Engine) -> None:

    metadata = sa.MetaData()
    sa.Table(
        "practice_people",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.VARCHAR(100)),
        sa.Column("age", sa.Integer),
        sa.Column("email", sa.Text),  # new column, only in Python
    )

    # The table already exists, so create_all skips it: no ALTER TABLE
    metadata.create_all(engine)
    print("python:  ", list(metadata.tables["practice_people"].c.keys()))
    print("postgres:", _db_columns(engine, "practice_people"))

    # To really change it: ALTER TABLE by hand (or Alembic later),
    # or drop + create again (loses the data)
    with engine.begin() as conn:
        conn.execute(sa.text("ALTER TABLE practice_people ADD COLUMN email text"))
    print("after ALTER:", _db_columns(engine, "practice_people"))

    # Back to the normal definition for the next phases
    metadata.tables["practice_people"].drop(engine)
    clean = sa.MetaData()
    _get_practice_people_table(clean, "practice_people")
    clean.create_all(engine)
    print("reset:   ", _db_columns(engine, "practice_people"))

    return None


# -------------------- main ----------------------------------------------


def main() -> None:

    engine: sa.Engine = get_engine()

    print("--- 1. defining is not creating")
    define_is_not_create(engine)
    print("--- 2. create_all")
    create_all_example(engine)
    print("--- 3. drop")
    drop_example(engine)
    print("--- 4. changing a Column later")
    change_column_later(engine)

    return None


# -------------------- end main ------------------------------------------


if __name__ == "__main__":
    main()
