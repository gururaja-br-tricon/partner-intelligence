import os

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

QUERY_LIMIT = 100

DATABASE = os.getenv("SNOWFLAKE_DATABASE", "PARTNER_INTELLIGENCE_DB")
# schemas
PARTNER_SCHEMA = f"{DATABASE}.PARTNER_DATA"
MARKET_SCHEMA = f"{DATABASE}.MARKET_DATA"
EVENT_SCHEMA = f"{DATABASE}.EVENT_DATA"
MATCHMAKING_SCHEMA = f"{DATABASE}.MATCHMAKING_DATA"
GTM_SCHEMA = f"{DATABASE}.GTM_DATA"

# tables
PARTNER_MASTER = f"{PARTNER_SCHEMA}.PARTNER_MASTER"
PARTNER_CAPABILITIES = f"{PARTNER_SCHEMA}.PARTNER_CAPABILITIES"
PARTNER_CLASSIFICATIONS = f"{PARTNER_SCHEMA}.PARTNER_CLASSIFICATIONS"
PARTNER_PROGRAMS = f"{PARTNER_SCHEMA}.PARTNER_PROGRAMS"
PARTNER_PERFORMANCE = f"{PARTNER_SCHEMA}.PARTNER_PERFORMANCE"

MARKETS = f"{MARKET_SCHEMA}.MARKETS"
MARKET_INTELLIGENCE = f"{MARKET_SCHEMA}.MARKET_INTELLIGENCE"

EVENTS = f"{EVENT_SCHEMA}.EVENTS"
EVENT_PARTICIPANTS = f"{EVENT_SCHEMA}.EVENT_PARTICIPANTS"

PARTNER_MATCHES = f"{MATCHMAKING_SCHEMA}.PARTNER_MATCHES"

GTM_OPPORTUNITIES = f"{GTM_SCHEMA}.GTM_OPPORTUNITIES"
GTM_RECOMMENDATIONS = f"{GTM_SCHEMA}.GTM_RECOMMENDATIONS"


class SnowflakeMarketRepository:

    def __init__(self):
        self.connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_MARKET_USER"),
            password=os.getenv("SNOWFLAKE_MARKET_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            role=os.getenv("SNOWFLAKE_MARKET_ROLE"),
        )

    def close(self):
        self.connection.close()

    def search_markets(
        self,
        market_name=None,
        market_category=None,
        region=None,
        technology=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT DISTINCT
                market_id,
                market_name,
                market_category,
                description,
                primary_technologies,
                market_priority,
                target_regions
            FROM {MARKETS}
            WHERE 1 = 1
        """

        parameters = []

        if market_name:
            query += " AND market_name = %s"
            parameters.append(market_name)

        if market_category:
            query += " AND market_category = %s"
            parameters.append(market_category)

        if region:
            query += " AND target_regions ILIKE %s"
            parameters.append(f"%{region}%")

        if technology:
            query += " AND primary_technologies ILIKE %s"
            parameters.append(f"%{technology}%")

        query += """
            ORDER BY market_name
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "market_category": row["MARKET_CATEGORY"],
                    "description": row["DESCRIPTION"],
                    "primary_technologies": row["PRIMARY_TECHNOLOGIES"],
                    "market_priority": row["MARKET_PRIORITY"],
                    "target_regions": row["TARGET_REGIONS"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def get_market_intelligence(
        self,
        market_id=None,
        region=None,
        country=None,
        industry=None,
        technology=None,
        analysis_year=None,
        demand_level=None,
        growth_level=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT
                market_intelligence_id,
                market_id,
                market_name,
                analysis_year,
                region,
                country,
                industry,
                technology,
                market_size_billion,
                market_growth_pct,
                tam_billion,
                sam_billion,
                som_billion,
                demand_score,
                technology_adoption_pct,
                competitive_intensity_score,
                active_partner_count,
                active_opportunity_count,
                demand_level,
                growth_level
            FROM {MARKET_INTELLIGENCE}
            WHERE 1 = 1
        """

        parameters = []

        if market_id:
            query += " AND market_id = %s"
            parameters.append(market_id)

        if region:
            query += " AND region = %s"
            parameters.append(region)

        if country:
            query += " AND country = %s"
            parameters.append(country)

        if industry:
            query += " AND industry = %s"
            parameters.append(industry)

        if technology:
            query += " AND technology = %s"
            parameters.append(technology)

        if analysis_year is not None:
            query += " AND analysis_year = %s"
            parameters.append(analysis_year)

        if demand_level:
            query += " AND demand_level = %s"
            parameters.append(demand_level)

        if growth_level:
            query += " AND growth_level = %s"
            parameters.append(growth_level)

        query += """
            ORDER BY
                market_growth_pct DESC,
                demand_score DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "market_intelligence_id": row["MARKET_INTELLIGENCE_ID"],
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "analysis_year": row["ANALYSIS_YEAR"],
                    "region": row["REGION"],
                    "country": row["COUNTRY"],
                    "industry": row["INDUSTRY"],
                    "technology": row["TECHNOLOGY"],
                    "market_size_billion": row["MARKET_SIZE_BILLION"],
                    "market_growth_pct": row["MARKET_GROWTH_PCT"],
                    "tam_billion": row["TAM_BILLION"],
                    "sam_billion": row["SAM_BILLION"],
                    "som_billion": row["SOM_BILLION"],
                    "demand_score": row["DEMAND_SCORE"],
                    "technology_adoption_pct": row["TECHNOLOGY_ADOPTION_PCT"],
                    "competitive_intensity_score": row["COMPETITIVE_INTENSITY_SCORE"],
                    "active_partner_count": row["ACTIVE_PARTNER_COUNT"],
                    "active_opportunity_count": row["ACTIVE_OPPORTUNITY_COUNT"],
                    "demand_level": row["DEMAND_LEVEL"],
                    "growth_level": row["GROWTH_LEVEL"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def compare_markets(
        self,
        market_ids,
        region=None,
        industry=None,
        technology=None,
        analysis_year=None,
    ):
        if not market_ids:
            return []

        placeholders = ", ".join(["%s"] * len(market_ids))

        query = f"""
            SELECT
                market_id,
                market_name,
                analysis_year,
                region,
                industry,
                technology,
                market_size_billion,
                market_growth_pct,
                tam_billion,
                sam_billion,
                som_billion,
                demand_score,
                technology_adoption_pct,
                competitive_intensity_score,
                active_partner_count,
                active_opportunity_count
            FROM {MARKET_INTELLIGENCE}
            WHERE market_id IN ({placeholders})
        """

        parameters = list(market_ids)

        if region:
            query += " AND region = %s"
            parameters.append(region)

        if industry:
            query += " AND industry = %s"
            parameters.append(industry)

        if technology:
            query += " AND technology = %s"
            parameters.append(technology)

        if analysis_year is not None:
            query += " AND analysis_year = %s"
            parameters.append(analysis_year)

        query += """
            ORDER BY
                market_growth_pct DESC,
                demand_score DESC
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "analysis_year": row["ANALYSIS_YEAR"],
                    "region": row["REGION"],
                    "industry": row["INDUSTRY"],
                    "technology": row["TECHNOLOGY"],
                    "market_size_billion": row["MARKET_SIZE_BILLION"],
                    "market_growth_pct": row["MARKET_GROWTH_PCT"],
                    "tam_billion": row["TAM_BILLION"],
                    "sam_billion": row["SAM_BILLION"],
                    "som_billion": row["SOM_BILLION"],
                    "demand_score": row["DEMAND_SCORE"],
                    "technology_adoption_pct": row["TECHNOLOGY_ADOPTION_PCT"],
                    "competitive_intensity_score": row["COMPETITIVE_INTENSITY_SCORE"],
                    "active_partner_count": row["ACTIVE_PARTNER_COUNT"],
                    "active_opportunity_count": row["ACTIVE_OPPORTUNITY_COUNT"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

if __name__ == "__main__":
    repository = SnowflakeMarketRepository()

    result = repository.search_markets(
        limit=5
    )

    for row in result:
        print(row)

    repository.close()
