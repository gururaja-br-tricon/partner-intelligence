import csv
import os
from pathlib import Path

import snowflake.connector

from dotenv import load_dotenv

load_dotenv()


DATABASE = "PARTNER_INTELLIGENCE_DB"

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"


# ------------------------------------------------------------------
# Snowflake configuration
# ------------------------------------------------------------------

SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": DATABASE,
}


# ------------------------------------------------------------------
# CSV -> Snowflake mapping
# ------------------------------------------------------------------

TABLES = {
    # "PARTNER_DATA": {
    #     "partner_master.csv": "PARTNER_MASTER",
    #     "partner_capabilities.csv": "PARTNER_CAPABILITIES",
    #     "partner_programs.csv": "PARTNER_PROGRAMS",
    #     "partner_classifications.csv": "PARTNER_CLASSIFICATIONS",
    #     "partner_performance.csv": "PARTNER_PERFORMANCE",
    # },
    "MARKET_DATA": {
        "markets.csv": "MARKETS",
        "market_intelligence.csv": "MARKET_INTELLIGENCE",
    },
    "EVENT_DATA": {
        "events.csv": "EVENTS",
        "event_participants.csv": "EVENT_PARTICIPANTS",
    },
    "MATCHMAKING_DATA": {
        "matching_criteria.csv": "MATCHING_CRITERIA",
        "partner_matches.csv": "PARTNER_MATCHES",
    },
    "GTM_DATA": {
        "gtm_opportunities.csv": "GTM_OPPORTUNITIES",
        "gtm_recommendations.csv": "GTM_RECOMMENDATIONS",
    },
}


def get_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
    )


def quote_identifier(name):
    return '"' + name.upper().replace('"', '""') + '"'


def create_schema(cursor, schema_name):
    sql = f"""
        CREATE SCHEMA IF NOT EXISTS
        {quote_identifier(DATABASE)}.{quote_identifier(schema_name)}
    """

    cursor.execute(sql)
    print(f"  Schema ready: {schema_name}")


def read_csv(file_path):
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        columns = reader.fieldnames

    return columns, rows


def infer_column_type(values):
    non_empty = [v for v in values if v not in (None, "")]

    if not non_empty:
        return "VARCHAR"

    # Integer
    try:
        for value in non_empty:
            int(value)
        return "INTEGER"
    except ValueError:
        pass

    # Decimal / floating point
    try:
        for value in non_empty:
            float(value)
        return "NUMBER(38, 4)"
    except ValueError:
        pass

    return "VARCHAR"


def create_table(cursor, schema_name, table_name, columns, rows):
    column_definitions = []

    for column in columns:
        values = [row[column] for row in rows]
        column_type = infer_column_type(values)

        column_definitions.append(f"{quote_identifier(column)} {column_type}")

    sql = f"""
        CREATE TABLE IF NOT EXISTS
        {quote_identifier(DATABASE)}.{quote_identifier(schema_name)}
        .{quote_identifier(table_name)}
        (
            {", ".join(column_definitions)}
        )
    """

    cursor.execute(sql)

    print(f"  Table ready: " f"{schema_name}.{table_name}")


def load_rows(cursor, schema_name, table_name, columns, rows):
    if not rows:
        print("  No rows to load")
        return 0

    column_list = ", ".join(quote_identifier(column) for column in columns)

    placeholders = ", ".join(["%s"] * len(columns))

    sql = f"""
        INSERT INTO
        {quote_identifier(DATABASE)}
        .{quote_identifier(schema_name)}
        .{quote_identifier(table_name)}
        ({column_list})
        VALUES ({placeholders})
    """

    values = []

    for row in rows:
        values.append(
            tuple(row[column] if row[column] != "" else None for column in columns)
        )

    cursor.executemany(sql, values)

    return len(values)


def load_table(cursor, schema_name, csv_file, table_name):
    file_path = DATA_DIR / csv_file

    if not file_path.exists():
        print(f"  SKIP: {file_path} does not exist")
        return 0

    columns, rows = read_csv(file_path)

    create_table(
        cursor,
        schema_name,
        table_name,
        columns,
        rows,
    )

    cursor.execute(f"""
        TRUNCATE TABLE
        {quote_identifier(DATABASE)}
        .{quote_identifier(schema_name)}
        .{quote_identifier(table_name)}
        """)

    count = load_rows(
        cursor,
        schema_name,
        table_name,
        columns,
        rows,
    )

    print(f"  Loaded {count} rows -> " f"{schema_name}.{table_name}")

    return count


def main():
    print("=" * 70)
    print("Snowflake data loader")
    print("=" * 70)

    missing = [key for key, value in SNOWFLAKE_CONFIG.items() if not value]

    if missing:
        raise RuntimeError(
            "Missing Snowflake environment variables: "
            + ", ".join(
                f"SNOWFLAKE_{key.upper()}" for key in missing if key != "database"
            )
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        total_rows = 0

        for schema_name, tables in TABLES.items():
            print()
            print(f"[{schema_name}]")

            create_schema(
                cursor,
                schema_name,
            )

            for csv_file, table_name in tables.items():
                count = load_table(
                    cursor,
                    schema_name,
                    csv_file,
                    table_name,
                )

                total_rows += count

        connection.commit()

        print()
        print("=" * 70)
        print(f"TOTAL ROWS LOADED: {total_rows}")
        print("=" * 70)

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
