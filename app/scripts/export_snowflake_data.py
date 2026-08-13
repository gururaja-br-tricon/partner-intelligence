import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv


load_dotenv()

OUTPUT_DIR = Path("snowflake_export")
OUTPUT_DIR.mkdir(exist_ok=True)


TABLES = {
    "PARTNER_DATA": [
        "PARTNER_MASTER",
        "PARTNER_CAPABILITIES",
        "PARTNER_CLASSIFICATIONS",
        "PARTNER_PROGRAMS",
        "PARTNER_PERFORMANCE",
    ],
    "MARKET_DATA": [
        "MARKETS",
        "MARKET_INTELLIGENCE",
    ],
    "EVENT_DATA": [
        "EVENTS",
        "EVENT_PARTICIPANTS",
    ],
    "MATCHMAKING_DATA": [
        "PARTNER_MATCHES",
    ],
    "GTM_DATA": [
        "GTM_OPPORTUNITIES",
        "GTM_RECOMMENDATIONS",
    ],
}


def export_table(cursor, schema, table):
    output_file = OUTPUT_DIR / f"{schema.lower()}_{table.lower()}.csv"

    query = f"""
        SELECT *
        FROM PARTNER_INTELLIGENCE_DB.{schema}.{table}
    """

    print(f"Exporting {schema}.{table}...")

    cursor.execute(query)

    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    with open(output_file, "w", encoding="utf-8", newline="") as file:
        file.write(",".join(columns) + "\n")

        for row in rows:
            values = []

            for value in row:
                if value is None:
                    values.append("")
                else:
                    value = str(value).replace('"', '""')
                    values.append(f'"{value}"')

            file.write(",".join(values) + "\n")

    print(f"  Rows: {len(rows)}")
    print(f"  File: {output_file}")


def main():
    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database="PARTNER_INTELLIGENCE_DB",
        role=os.getenv("SNOWFLAKE_ROLE"),
    )

    cursor = connection.cursor()

    try:
        for schema, tables in TABLES.items():
            for table in tables:
                export_table(cursor, schema, table)

    finally:
        cursor.close()
        connection.close()

    print("\nExport complete.")


if __name__ == "__main__":
    main()