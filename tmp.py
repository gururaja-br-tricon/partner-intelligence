"""
Extract categorical/enum values from all Snowflake tables for docstring updates.

This script connects using domain-specific roles (PARTNER_ROLE, MARKET_ROLE, EVENT_ROLE, GTM_ROLE)
to access different schemas and extracts all distinct values from categorical columns.

Usage:
    python extract_categorical_values.py

Output:
    - Prints formatted output ready for docstring copy-paste
    - Groups by domain for easy navigation
    - Shows which role was used for each query

Requirements:
    - .env file with Snowflake credentials and roles
    - snowflake-connector-python
"""

import os
import snowflake.connector
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

DATABASE = os.getenv("SNOWFLAKE_DATABASE", "PARTNER_INTELLIGENCE_DB")
PARTNER_SCHEMA = f"{DATABASE}.PARTNER_DATA"
MARKET_SCHEMA = f"{DATABASE}.MARKET_DATA"
EVENT_SCHEMA = f"{DATABASE}.EVENT_DATA"
MATCHMAKING_SCHEMA = f"{DATABASE}.MATCHMAKING_DATA"
GTM_SCHEMA = f"{DATABASE}.GTM_DATA"

# Domain to role mapping - adjust if your roles have different names
DOMAIN_ROLES = {
    "PARTNER": os.getenv("SNOWFLAKE_PARTNER_ROLE", "PARTNER_ROLE"),
    "MARKET": os.getenv("SNOWFLAKE_MARKET_ROLE", "MARKET_ROLE"),
    "EVENT": os.getenv("SNOWFLAKE_EVENT_ROLE", "EVENT_ROLE"),
    "GTM": os.getenv("SNOWFLAKE_GTM_ROLE", "GTM_ROLE"),
}

# Table definitions with columns to extract
TABLES_TO_EXTRACT = {
    "PARTNER_MASTER": {
        "domain": "PARTNER",
        "table": f"{PARTNER_SCHEMA}.PARTNER_MASTER",
        "columns": ["status"],
    },
    "PARTNER_CAPABILITIES": {
        "domain": "PARTNER",
        "table": f"{PARTNER_SCHEMA}.PARTNER_CAPABILITIES",
        "columns": ["capability", "proficiency_level"],
    },
    "PARTNER_CLASSIFICATIONS": {
        "domain": "PARTNER",
        "table": f"{PARTNER_SCHEMA}.PARTNER_CLASSIFICATIONS",
        "columns": ["classification"],
    },
    "PARTNER_PROGRAMS": {
        "domain": "PARTNER",
        "table": f"{PARTNER_SCHEMA}.PARTNER_PROGRAMS",
        "columns": ["vendor", "program_name", "partner_tier"],
    },
    "PARTNER_PERFORMANCE": {
        "domain": "PARTNER",
        "table": f"{PARTNER_SCHEMA}.PARTNER_PERFORMANCE",
        "columns": ["performance_status"],
    },
    "MARKETS": {
        "domain": "MARKET",
        "table": f"{MARKET_SCHEMA}.MARKETS",
        "columns": ["market_category"],
    },
    "MARKET_INTELLIGENCE": {
        "domain": "MARKET",
        "table": f"{MARKET_SCHEMA}.MARKET_INTELLIGENCE",
        "columns": ["demand_level", "growth_level"],
    },
    "EVENTS": {
        "domain": "EVENT",
        "table": f"{EVENT_SCHEMA}.EVENTS",
        "columns": ["event_type", "event_status"],
    },
    "EVENT_PARTICIPANTS": {
        "domain": "EVENT",
        "table": f"{EVENT_SCHEMA}.EVENT_PARTICIPANTS",
        "columns": ["participation_type"],
    },
    "PARTNER_MATCHES": {
        "domain": "EVENT",
        "table": f"{MATCHMAKING_SCHEMA}.PARTNER_MATCHES",
        "columns": ["match_status"],
    },
    "GTM_OPPORTUNITIES": {
        "domain": "GTM",
        "table": f"{GTM_SCHEMA}.GTM_OPPORTUNITIES",
        "columns": ["opportunity_type", "priority", "opportunity_status"],
    },
    "GTM_RECOMMENDATIONS": {
        "domain": "GTM",
        "table": f"{GTM_SCHEMA}.GTM_RECOMMENDATIONS",
        "columns": ["recommendation_type", "status"],
    },
}


def get_connection(domain):
    """Create a Snowflake connection using domain-specific role"""
    role = DOMAIN_ROLES.get(domain)
    if not role:
        raise ValueError(
            f"Unknown domain: {domain}. Available: {list(DOMAIN_ROLES.keys())}"
        )
    # import ipdb; ipdb.set_trace()
    if role == "PARTNER_DOMAIN_ROLE":
        user = os.getenv("SNOWFLAKE_PARTNER_USER")
        password = os.getenv("SNOWFLAKE_PARTNER_PASSWORD")
    if role == "MARKET_DOMAIN_ROLE":
        user = os.getenv("SNOWFLAKE_MARKET_USER")
        password = os.getenv("SNOWFLAKE_MARKET_PASSWORD")
    elif role == "EVENT_DOMAIN_ROLE":
        user = os.getenv("SNOWFLAKE_EVENT_USER")
        password = os.getenv("SNOWFLAKE_EVENT_PASSWORD")
    elif role == "GTM_DOMAIN_ROLE":
        user = os.getenv("SNOWFLAKE_GTM_USER")
        password = os.getenv("SNOWFLAKE_GTM_PASSWORD")

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=user,
        password=password,
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=DATABASE,
        role=role,
    )


def extract_column_values(connection, table_name, column_name):
    """Query distinct values from a column, returns sorted list"""
    query = f"""
        SELECT DISTINCT {column_name}
        FROM {table_name}
        WHERE {column_name} IS NOT NULL
        ORDER BY {column_name}
    """

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [row[0] for row in rows if row[0] is not None]
    except Exception as e:
        print(f"  ✗ ERROR extracting {column_name}: {e}")
        return None  # Return None to indicate error, not empty list
    finally:
        cursor.close()


def format_values_for_docstring(values):
    """Format list of values for docstring inclusion"""
    if not values:
        return "(no values found)"
    return ", ".join(str(v) for v in values)


def main():
    print("\n" + "=" * 90)
    print("SNOWFLAKE CATEGORICAL VALUES EXTRACTOR")
    print("=" * 90)
    print(f"Database: {DATABASE}")
    print(f"Account: {os.getenv('SNOWFLAKE_ACCOUNT')}")
    print()

    # Track results by domain and table
    results = defaultdict(lambda: defaultdict(dict))
    connections = {}

    try:
        # Process each table
        for table_name, config in TABLES_TO_EXTRACT.items():
            domain = config["domain"]
            table_path = config["table"]
            columns = config["columns"]

            # Get or create connection for this domain
            if domain not in connections:
                try:
                    connections[domain] = get_connection(domain)
                    print(
                        f"✓ Connected to {domain} domain (role: {DOMAIN_ROLES[domain]})"
                    )
                except Exception as e:
                    print(f"✗ Failed to connect to {domain}: {e}")
                    continue

            connection = connections[domain]

            # Extract values from each column
            print(f"\n  {table_name}:")
            for column_name in columns:
                values = extract_column_values(connection, table_path, column_name)

                if values is None:
                    print(f"    {column_name}: (column not found or query failed)")
                    # Still store it but mark as error
                    results[domain][table_name][column_name] = []
                else:
                    results[domain][table_name][column_name] = values
                    value_str = format_values_for_docstring(values)
                    print(f"    {column_name}: {value_str}")

        # Print formatted output for docstrings
        print("\n\n" + "=" * 90)
        print("FORMATTED OUTPUT FOR DOCSTRINGS (COPY-PASTE READY)")
        print("=" * 90)

        # PARTNER DOMAIN
        print("\n" + "-" * 90)
        print("PARTNER DOMAIN - search_partners()")
        print("-" * 90)
        
        # Helper function to safely print values
        def print_column_values(domain, table, column):
            if (
                domain in results
                and table in results[domain]
                and column in results[domain][table]
            ):
                vals = results[domain][table][column]
                print(f"\n{column}:")
                if vals:
                    for val in vals:
                        print(f"    {val}")
                else:
                    print(f"    (no values found)")
            else:
                print(f"\n{column}: (column not found or query failed)")

        print_column_values("PARTNER", "PARTNER_MASTER", "status")
        print_column_values("PARTNER", "PARTNER_CAPABILITIES", "capability")
        print_column_values("PARTNER", "PARTNER_CAPABILITIES", "proficiency_level")
        print_column_values("PARTNER", "PARTNER_PROGRAMS", "vendor")
        print_column_values("PARTNER", "PARTNER_PROGRAMS", "program_name")
        print_column_values("PARTNER", "PARTNER_PROGRAMS", "partner_tier")
        print_column_values("PARTNER", "PARTNER_CLASSIFICATIONS", "classification")
        print_column_values("PARTNER", "PARTNER_PERFORMANCE", "performance_status")

        # MARKET DOMAIN
        print("\n" + "-" * 90)
        print("MARKET DOMAIN - search_markets()")
        print("-" * 90)

        if (
            "MARKETS" in results["MARKET"]
            and "market_category" in results["MARKET"]["MARKETS"]
        ):
            print("\nmarket_category:")
            for val in results["MARKET"]["MARKETS"]["market_category"]:
                print(f"    {val}")
        else:
            print("\nmarket_category: (column not found)")

        if (
            "MARKET_INTELLIGENCE" in results["MARKET"]
            and "demand_level" in results["MARKET"]["MARKET_INTELLIGENCE"]
        ):
            print("\ndemand_level:")
            for val in results["MARKET"]["MARKET_INTELLIGENCE"]["demand_level"]:
                print(f"    {val}")
        else:
            print("\ndemand_level: (column not found)")

        if (
            "MARKET_INTELLIGENCE" in results["MARKET"]
            and "growth_level" in results["MARKET"]["MARKET_INTELLIGENCE"]
        ):
            print("\ngrowth_level:")
            for val in results["MARKET"]["MARKET_INTELLIGENCE"]["growth_level"]:
                print(f"    {val}")
        else:
            print("\ngrowth_level: (column not found)")

        # EVENT DOMAIN
        print("\n" + "-" * 90)
        print("EVENT DOMAIN - search_events() & find_partner_matches()")
        print("-" * 90)

        print_column_values("EVENT", "EVENTS", "event_type")
        print_column_values("EVENT", "EVENTS", "event_status")
        print_column_values("EVENT", "EVENT_PARTICIPANTS", "participation_type")
        print_column_values("EVENT", "PARTNER_MATCHES", "match_status")

        # GTM DOMAIN
        print("\n" + "-" * 90)
        print("GTM DOMAIN - search_gtm_opportunities()")
        print("-" * 90)

        print_column_values("GTM", "GTM_OPPORTUNITIES", "opportunity_type")
        print_column_values("GTM", "GTM_OPPORTUNITIES", "priority")
        print_column_values("GTM", "GTM_OPPORTUNITIES", "opportunity_status")
        print_column_values("GTM", "GTM_RECOMMENDATIONS", "recommendation_type")
        print_column_values("GTM", "GTM_RECOMMENDATIONS", "status")

        # Print Python dict format for easy programmatic use
        print("\n\n" + "=" * 90)
        print("PYTHON DICT FORMAT (FOR PROGRAMMATIC USE)")
        print("=" * 90)
        print("\nresults = {")
        for domain in ["PARTNER", "MARKET", "EVENT", "GTM"]:
            print(f'    "{domain}": {{')
            for table_name in sorted(results[domain].keys()):
                print(f'        "{table_name}": {{')
                for column_name in sorted(results[domain][table_name].keys()):
                    values = results[domain][table_name][column_name]
                    values_repr = repr(values)
                    print(f'            "{column_name}": {values_repr},')
                print("        },")
            print("    },")
        print("}")

        print("\n" + "=" * 90)
        print("EXTRACTION COMPLETE")
        print("=" * 90 + "\n")

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Close all connections
        for domain, conn in connections.items():
            try:
                conn.close()
                print(f"✓ Closed {domain} connection")
            except:
                pass


if __name__ == "__main__":
    main()
