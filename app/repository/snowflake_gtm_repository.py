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


class SnowflakeGTMRepository:

    def __init__(self):
        self.connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_GTM_USER"),
            password=os.getenv("SNOWFLAKE_GTM_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            role=os.getenv("SNOWFLAKE_GTM_ROLE"),
        )

    def close(self):
        self.connection.close()

    def search_gtm_opportunities(
        self,
        partner_id=None,
        market_id=None,
        region=None,
        industry=None,
        technology=None,
        opportunity_type=None,
        priority=None,
        opportunity_status=None,
        analysis_year=None,
        min_opportunity_value=None,
        min_win_probability=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT
                GTM_OPPORTUNITY_ID,
                PARTNER_ID,
                MARKET_ID,
                MARKET_NAME,
                REGION,
                INDUSTRY,
                TECHNOLOGY,
                OPPORTUNITY_TYPE,
                ESTIMATED_OPPORTUNITY_VALUE,
                MARKET_GROWTH_PCT,
                DEMAND_GROWTH_PCT,
                PARTNER_FIT_SCORE,
                COMPETITIVE_INTENSITY,
                WIN_PROBABILITY_PCT,
                PRIORITY,
                RECOMMENDED_ACTION,
                OPPORTUNITY_STATUS,
                ANALYSIS_YEAR
            FROM {GTM_OPPORTUNITIES}
            WHERE 1 = 1
        """

        parameters = []

        if partner_id:
            query += " AND PARTNER_ID = %s"
            parameters.append(partner_id)

        if market_id:
            query += " AND MARKET_ID = %s"
            parameters.append(market_id)

        if region:
            query += " AND REGION = %s"
            parameters.append(region)

        if industry:
            query += " AND INDUSTRY = %s"
            parameters.append(industry)

        if technology:
            query += " AND TECHNOLOGY = %s"
            parameters.append(technology)

        if opportunity_type:
            query += " AND OPPORTUNITY_TYPE = %s"
            parameters.append(opportunity_type)

        if priority:
            query += " AND PRIORITY = %s"
            parameters.append(priority)

        if opportunity_status:
            query += " AND OPPORTUNITY_STATUS = %s"
            parameters.append(opportunity_status)

        if analysis_year is not None:
            query += " AND ANALYSIS_YEAR = %s"
            parameters.append(analysis_year)

        if min_opportunity_value is not None:
            query += " AND ESTIMATED_OPPORTUNITY_VALUE >= %s"
            parameters.append(min_opportunity_value)

        if min_win_probability is not None:
            query += " AND WIN_PROBABILITY_PCT >= %s"
            parameters.append(min_win_probability)

        query += """
            ORDER BY
                PRIORITY,
                WIN_PROBABILITY_PCT DESC,
                ESTIMATED_OPPORTUNITY_VALUE DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "gtm_opportunity_id": row["GTM_OPPORTUNITY_ID"],
                    "partner_id": row["PARTNER_ID"],
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "region": row["REGION"],
                    "industry": row["INDUSTRY"],
                    "technology": row["TECHNOLOGY"],
                    "opportunity_type": row["OPPORTUNITY_TYPE"],
                    "estimated_opportunity_value": row["ESTIMATED_OPPORTUNITY_VALUE"],
                    "market_growth_pct": row["MARKET_GROWTH_PCT"],
                    "demand_growth_pct": row["DEMAND_GROWTH_PCT"],
                    "partner_fit_score": row["PARTNER_FIT_SCORE"],
                    "competitive_intensity": row["COMPETITIVE_INTENSITY"],
                    "win_probability_pct": row["WIN_PROBABILITY_PCT"],
                    "priority": row["PRIORITY"],
                    "recommended_action": row["RECOMMENDED_ACTION"],
                    "opportunity_status": row["OPPORTUNITY_STATUS"],
                    "analysis_year": row["ANALYSIS_YEAR"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def get_gtm_recommendations(
        self,
        partner_id=None,
        market_id=None,
        region=None,
        industry=None,
        technology=None,
        recommendation_type=None,
        status=None,
        min_recommendation_score=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT
                RECOMMENDATION_ID,
                PARTNER_ID,
                MARKET_ID,
                MARKET_NAME,
                REGION,
                INDUSTRY,
                TECHNOLOGY,
                RECOMMENDATION_TYPE,
                RECOMMENDATION_SCORE,
                RATIONALE,
                EXPECTED_IMPACT,
                RECOMMENDED_TIMEFRAME,
                STATUS
            FROM {GTM_RECOMMENDATIONS}
            WHERE 1 = 1
        """

        parameters = []

        if partner_id:
            query += " AND PARTNER_ID = %s"
            parameters.append(partner_id)

        if market_id:
            query += " AND MARKET_ID = %s"
            parameters.append(market_id)

        if region:
            query += " AND REGION = %s"
            parameters.append(region)

        if industry:
            query += " AND INDUSTRY = %s"
            parameters.append(industry)

        if technology:
            query += " AND TECHNOLOGY = %s"
            parameters.append(technology)

        if recommendation_type:
            query += " AND RECOMMENDATION_TYPE = %s"
            parameters.append(recommendation_type)

        if status:
            query += " AND STATUS = %s"
            parameters.append(status)

        if min_recommendation_score is not None:
            query += " AND RECOMMENDATION_SCORE >= %s"
            parameters.append(min_recommendation_score)

        query += """
            ORDER BY RECOMMENDATION_SCORE DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "recommendation_id": row["RECOMMENDATION_ID"],
                    "partner_id": row["PARTNER_ID"],
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "region": row["REGION"],
                    "industry": row["INDUSTRY"],
                    "technology": row["TECHNOLOGY"],
                    "recommendation_type": row["RECOMMENDATION_TYPE"],
                    "recommendation_score": row["RECOMMENDATION_SCORE"],
                    "rationale": row["RATIONALE"],
                    "expected_impact": row["EXPECTED_IMPACT"],
                    "recommended_timeframe": row["RECOMMENDED_TIMEFRAME"],
                    "status": row["STATUS"],
                }
                for row in rows
            ]

        finally:
            cursor.close()


if __name__ == "__main__":
    repository = SnowflakeGTMRepository()

    result = repository.get_gtm_recommendations(
        limit=10
    )

    for row in result:
        print(row)

    repository.close()
