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

    # ============================================================================
    # CONSOLIDATED METHOD: search_markets now includes intelligence filters
    # REMOVES: get_market_intelligence (old separate method)
    # ============================================================================
    def search_markets(
        self,
        market_name=None,
        market_category=None,
        region=None,
        technology=None,
        # NEW: Intelligence filters (from old get_market_intelligence)
        market_id=None,
        country=None,
        industry=None,
        analysis_year=None,
        demand_level=None,
        growth_level=None,
        include_intelligence=False,  # Flag to add intelligence columns
        limit=QUERY_LIMIT,
    ):
        """
        Search markets with optional intelligence data.
        
        This method consolidates search_markets + get_market_intelligence.
        If include_intelligence=True or intelligence filters are provided,
        it joins MARKET_INTELLIGENCE and returns analytical metrics.
        """
        
        has_intel_filters = any([
            market_id is not None,
            country is not None,
            industry is not None,
            analysis_year is not None,
            demand_level is not None,
            growth_level is not None,
        ])

        query = f"""
            SELECT DISTINCT
                m.market_id,
                m.market_name,
                m.market_category,
                m.description,
                m.primary_technologies,
                m.market_priority,
                m.target_regions
        """

        # Add intelligence columns if requested
        if include_intelligence or has_intel_filters:
            query += """
                , mi.market_intelligence_id,
                mi.analysis_year,
                mi.market_size_billion,
                mi.market_growth_pct,
                mi.tam_billion,
                mi.sam_billion,
                mi.som_billion,
                mi.demand_score,
                mi.technology_adoption_pct,
                mi.competitive_intensity_score,
                mi.active_partner_count,
                mi.active_opportunity_count,
                mi.demand_level,
                mi.growth_level
            """

        query += f"""
            FROM {MARKETS} m
        """

        # Add intelligence join if needed
        if include_intelligence or has_intel_filters:
            query += f"""
            LEFT JOIN {MARKET_INTELLIGENCE} mi
                ON m.market_id = mi.market_id
            """

        query += " WHERE 1 = 1"

        parameters = []

        # Original market definition filters
        if market_name:
            query += " AND m.market_name = %s"
            parameters.append(market_name)

        if market_category:
            query += " AND m.market_category = %s"
            parameters.append(market_category)

        if region:
            query += " AND m.target_regions ILIKE %s"
            parameters.append(f"%{region}%")

        if technology:
            query += " AND m.primary_technologies ILIKE %s"
            parameters.append(f"%{technology}%")

        # NEW: Intelligence filters
        if market_id:
            query += " AND m.market_id = %s"
            parameters.append(market_id)

        if country:
            query += " AND mi.country = %s"
            parameters.append(country)

        if industry:
            query += " AND mi.industry = %s"
            parameters.append(industry)

        if analysis_year is not None:
            query += " AND mi.analysis_year = %s"
            parameters.append(analysis_year)

        if demand_level:
            query += " AND mi.demand_level = %s"
            parameters.append(demand_level)

        if growth_level:
            query += " AND mi.growth_level = %s"
            parameters.append(growth_level)

        query += """
            ORDER BY
        """

        if include_intelligence or has_intel_filters:
            query += """
                mi.market_growth_pct DESC,
                mi.demand_score DESC
            """
        else:
            query += " m.market_name"

        if limit:
            query += " LIMIT %s"
            parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                market_dict = {
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "market_category": row["MARKET_CATEGORY"],
                    "description": row["DESCRIPTION"],
                    "primary_technologies": row["PRIMARY_TECHNOLOGIES"],
                    "market_priority": row["MARKET_PRIORITY"],
                    "target_regions": row["TARGET_REGIONS"],
                }

                # Add intelligence data if available
                if include_intelligence or has_intel_filters:
                    market_dict.update({
                        "market_intelligence_id": row["MARKET_INTELLIGENCE_ID"],
                        "analysis_year": row["ANALYSIS_YEAR"],
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
                    })

                result.append(market_dict)

            return result

        finally:
            cursor.close()

    # ============================================================================
    # KEEP: compare_markets (distinct use case, still used for side-by-side analysis)
    # ============================================================================
    def compare_markets(
        self,
        market_ids,
        region=None,
        industry=None,
        technology=None,
        analysis_year=None,
    ):
        """
        Compare multiple markets side-by-side using intelligence data.
        Still a separate method because it has a distinct input pattern (list of IDs).
        """
        if not market_ids:
            return []

        placeholders = ", ".join(["%s"] * len(market_ids))

        query = f"""
            SELECT
                m.market_id,
                m.market_name,
                mi.analysis_year,
                mi.region,
                mi.industry,
                mi.technology,
                mi.market_size_billion,
                mi.market_growth_pct,
                mi.tam_billion,
                mi.sam_billion,
                mi.som_billion,
                mi.demand_score,
                mi.technology_adoption_pct,
                mi.competitive_intensity_score,
                mi.active_partner_count,
                mi.active_opportunity_count
            FROM {MARKETS} m
            LEFT JOIN {MARKET_INTELLIGENCE} mi
                ON m.market_id = mi.market_id
            WHERE m.market_id IN ({placeholders})
        """

        parameters = list(market_ids)

        if region:
            query += " AND mi.region = %s"
            parameters.append(region)

        if industry:
            query += " AND mi.industry = %s"
            parameters.append(industry)

        if technology:
            query += " AND mi.technology = %s"
            parameters.append(technology)

        if analysis_year is not None:
            query += " AND mi.analysis_year = %s"
            parameters.append(analysis_year)

        query += """
            ORDER BY
                mi.market_growth_pct DESC,
                mi.demand_score DESC
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

    # Old way: two separate calls
    # result1 = repository.search_markets(market_name="Cloud")
    # result2 = repository.get_market_intelligence(region="EMEA", analysis_year=2026)

    # New way: one call with intelligence included
    result = repository.search_markets(
        technology="AI",
        include_intelligence=True,
        analysis_year=2026,
        limit=5
    )

    for row in result:
        print(row)

    repository.close()