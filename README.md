# psycopg + SQLAlchemy

Learning Postgres from Python, bottom up: the raw driver first (psycopg 3),
then SQLAlchemy Core, then the ORM, then transactions and performance.
The data is the e-commerce event dataset from the 42 Data Science piscine.

The full plan, the roadmaps and my notes live in my private Obsidian vault
(`Study plan`, `Psycopg roadmap`, `Core roadmap`, one note per phase), so they
are not in this repo.

## Progress

| Stage | Folder | Status |
| --- | --- | --- |
| 1. psycopg | [1-psycopg/](1-psycopg/) | done |
| 2. SQLAlchemy Core | [2-sqlalchemy-core/](2-sqlalchemy-core/) | in progress (phase 5 of 10: select) |
| 3. SQLAlchemy ORM | `3-sqlalchemy-orm/` | not started |
| 4. Transactions and performance | `4-performance/` | not started |
| 5. Final project (optional) | `5-project/` | not started |

### Stage 2: SQLAlchemy Core

| File | Phase |
| --- | --- |
| `01_engine.py` | `create_engine`, `URL.create`, the lazy engine |
| `02_connections.py` | `connect()` vs `begin()`, `Result`, rows |
| `03_tables.py` | `MetaData`, `Table`, `Column`, types, `table.c`, loading `practice_events` with `COPY` |
| `04_create.py` | `create_all`, `drop_all`, `table.drop(checkfirst=True)`, why a changed `Column` needs an `ALTER TABLE` |

Core uses psycopg 3 underneath (`postgresql+psycopg://`).

## Setup

Needs Docker and Python 3 with psycopg 3 and SQLAlchemy 2.

1. Create the two secret files next to `docker-compose.yml`, each holding just
   a password. They are not in git; start from the examples:

   ```bash
   cp db_password.txt.example db_password.txt
   cp pgadmin_password.txt.example pgadmin_password.txt
   ```

2. Start Postgres and pgAdmin:

   ```bash
   docker compose up -d
   ```

3. Install the driver and SQLAlchemy:

   ```bash
   pip install "psycopg[binary]" sqlalchemy
   ```

4. Run a script from inside its stage folder (the scripts read
   `../db_password.txt`, so the working directory matters):

   ```bash
   cd 2-sqlalchemy-core && python 03_tables.py
   ```

The CSV data is not in git. Put the piscine CSVs in `csv/customer/` and
`csv/item/`, next to `docker-compose.yml`. Both containers mount it with the
relative path `./csv/:/data`. If your CSVs live somewhere else, change that
path in `docker-compose.yml` (services `postgres` and `pgadmin`).

## Connection

| | Postgres | pgAdmin |
| --- | --- | --- |
| URL / host | `localhost:4242` | <http://localhost:8080> |
| User | `hbourlot` | `admin@example.com` |
| Password | `db_password.txt` | `pgadmin_password.txt` |
| Database | `piscineds` | |

To register the server inside pgAdmin, use host `postgres` and port `5432`
(the container-to-container address, not the published one).

## Data

`csv/` is mounted in the Postgres container at `/data`, so `COPY` can read the
files server-side.

| File | Rows | Columns |
| --- | --- | --- |
| `csv/customer/data_2022_oct.csv` | 4.1M | `event_time, event_type, product_id, price, user_id, user_session` |
| `csv/customer/data_2022_nov.csv` | 4.6M | same |
| `csv/customer/data_2022_dec.csv` | 3.5M | same |
| `csv/customer/data_2023_jan.csv` | 4.3M | same |
| `csv/customer/data_2023_feb.csv` | 4.2M | same |
| `csv/item/item.csv` | 110K | `product_id, category_id, category_code, brand` |

Loading one month:

```sql
CREATE TABLE data_2022_oct (
    event_time   timestamptz,
    event_type   text,
    product_id   integer,
    price        numeric(10,2),
    user_id      bigint,
    user_session uuid
);

COPY data_2022_oct
FROM '/data/customer/data_2022_oct.csv'
WITH (FORMAT csv, HEADER);
```

## Rules

- One numbered file per concept, one note per stage in the Obsidian vault.
- Practice tables are named `practice_*`. The `data_*` tables are only
  (re)created by the exercise scripts (`ex*.py`), never edited by hand.
- A stage is done when its checkpoint works without help.
