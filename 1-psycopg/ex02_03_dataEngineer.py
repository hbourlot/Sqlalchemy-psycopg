import psycopg as pg
from psycopg import sql
from pathlib import Path


def read_password(path: str) -> str:
    """Read a password from a file.

    Args:
        path (str): Path to the password file.

    Returns:
        str: File content with surrounding whitespace stripped.
    """
    with open(path) as f:
        return f.read().strip()


def get_settings() -> dict:
    """Return the PostgreSQL connection settings.

    Returns:
        dict: Keyword arguments for psycopg.connect().
    """
    return {
        "dbname": "piscineds",
        "user": "hbourlot",
        "password": read_password("../db_password.txt"),
        "host": "localhost",
        "port": "4242",
    }


def _create_table(cur: pg.Cursor, table: str) -> None:
    """Create the events table if it does not exist.

    Args:
        cur (pg.Cursor): Open cursor to execute on.
        table (str): Name of the table to create.
    """
    cur.execute(sql.SQL("""
                        CREATE TABLE IF NOT EXISTS {} (
                        event_time      TIMESTAMP,
                        event_type      VARCHAR(50),
                        product_id      INTEGER,
                        price           NUMERIC(10, 2),
                        user_id         bigint,
                        user_session    UUID)""").format(sql.Identifier(table)))

    return None


def _drop_table(cur: pg.Cursor, table: str) -> None:

    cur.execute(sql.SQL("""
                        DROP TABLE IF EXISTS {}""").format(sql.Identifier(table)))


def _load_csv(cur: pg.Cursor, table: str, csv_path: Path) -> None:
    """Bulk-load a CSV file into a table with COPY, streamed in 1MB chunks.

    The CSV must have a header row and columns in the table's order.

    Args:
        cur (pg.Cursor): Open cursor to execute on.
        table (str): Name of the target table.
        csv_path (str): Path to the CSV file.
    """
    with open(csv_path) as file:
        with cur.copy(
            sql.SQL("COPY {table} FROM STDIN WITH CSV HEADER").format(
                table=sql.Identifier(table)
            )
        ) as copy:
            while data := file.read(1024 * 1024):  # 1MB
                copy.write(data)

    return None


def _get_all_csv_paths(folder_path: str):

    all_paths: list[Path] = []
    for file in Path(folder_path).glob("*.csv"):
        if file.stem.startswith("data_202"):
            all_paths.append(file)

    return all_paths


def main() -> None:
    """Create the table and load the October 2022 CSV into it."""
    settings: dict = get_settings()

    # main_table: str = "customer"
    all_tables: list[Path] = _get_all_csv_paths("../csv/customer")

    with pg.connect(**settings) as conn:

        try:
            with conn.cursor() as cur:
                for csv_path in all_tables:
                    _drop_table(cur, csv_path.stem)
                    _create_table(cur, csv_path.stem)
                    _load_csv(cur, csv_path.stem, csv_path)

            # Quick check: row count and first row of each loaded table
            with conn.cursor() as src:
                for csv_path in all_tables:
                    src.execute(
                        sql.SQL("SELECT COUNT(*) FROM {}").format(
                            sql.Identifier(csv_path.stem)
                        )
                    )
                    print(f"{csv_path.stem}: {src.fetchone()[0]} rows")

                src.execute(
                    sql.SQL("SELECT * FROM {} LIMIT 1").format(
                        sql.Identifier(all_tables[0].stem)
                    )
                )
                print(src.fetchone())

        except pg.Error as e:
            print(f"{type(e).__name__} : {e}")

    return None


if __name__ == "__main__":
    main()
