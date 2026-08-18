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

    # ============================================================================
    # CONSOLIDATED METHOD: search_gtm_opportunities now includes recommendations
    # REMOVES: get_gtm_recommendations (old separate method)
    # ============================================================================
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
        # NEW: Recommendation filters (from old get_gtm_recommendations)
        recommendation_type=None,
        recommendation_status=None,
        min_recommendation_score=None,
        include_recommendations=False,  # Flag to include recommendation details
        limit=QUERY_LIMIT,
    ):
        """
        Search GTM opportunities with optional recommendation data.
        
        This method consolidates search_gtm_opportunities + get_gtm_recommendations.
        If include_recommendations=True or recommendation filters are provided,
        it joins GTM_RECOMMENDATIONS and returns action/impact data.
        """
        
        has_rec_filters = any([
            recommendation_type is not None,
            recommendation_status is not None,
            min_recommendation_score is not None,
            include_recommendations is True,
        ])

        query = f"""
            SELECT
                o.GTM_OPPORTUNITY_ID,
                o.PARTNER_ID,
                o.MARKET_ID,
                o.MARKET_NAME,
                o.REGION,
                o.INDUSTRY,
                o.TECHNOLOGY,
                o.OPPORTUNITY_TYPE,
                o.ESTIMATED_OPPORTUNITY_VALUE,
                o.MARKET_GROWTH_PCT,
                o.DEMAND_GROWTH_PCT,
                o.PARTNER_FIT_SCORE,
                o.COMPETITIVE_INTENSITY,
                o.WIN_PROBABILITY_PCT,
                o.PRIORITY,
                o.RECOMMENDED_ACTION,
                o.OPPORTUNITY_STATUS,
                o.ANALYSIS_YEAR
        """

        # Add recommendation columns if requested
        if has_rec_filters:
            query += """
                , r.RECOMMENDATION_ID,
                r.RECOMMENDATION_TYPE,
                r.RECOMMENDATION_SCORE,
                r.RATIONALE,
                r.EXPECTED_IMPACT,
                r.RECOMMENDED_TIMEFRAME,
                r.STATUS as RECOMMENDATION_STATUS
            """

        query += f"""
            FROM {GTM_OPPORTUNITIES} o
        """

        # Add recommendation join if needed
        if has_rec_filters:
            query += f"""
            LEFT JOIN {GTM_RECOMMENDATIONS} r
                ON o.PARTNER_ID = r.PARTNER_ID
                AND o.MARKET_ID = r.MARKET_ID
            """

        query += " WHERE 1 = 1"

        parameters = []

        # Opportunity filters
        if partner_id:
            query += " AND o.PARTNER_ID = %s"
            parameters.append(partner_id)

        if market_id:
            query += " AND o.MARKET_ID = %s"
            parameters.append(market_id)

        if region:
            query += " AND o.REGION = %s"
            parameters.append(region)

        if industry:
            query += " AND o.INDUSTRY = %s"
            parameters.append(industry)

        if technology:
            query += " AND o.TECHNOLOGY = %s"
            parameters.append(technology)

        if opportunity_type:
            query += " AND o.OPPORTUNITY_TYPE = %s"
            parameters.append(opportunity_type)

        if priority:
            query += " AND o.PRIORITY = %s"
            parameters.append(priority)

        if opportunity_status:
            query += " AND o.OPPORTUNITY_STATUS = %s"
            parameters.append(opportunity_status)

        if analysis_year is not None:
            query += " AND o.ANALYSIS_YEAR = %s"
            parameters.append(analysis_year)

        if min_opportunity_value is not None:
            query += " AND o.ESTIMATED_OPPORTUNITY_VALUE >= %s"
            parameters.append(min_opportunity_value)

        if min_win_probability is not None:
            query += " AND o.WIN_PROBABILITY_PCT >= %s"
            parameters.append(min_win_probability)

        # NEW: Recommendation filters
        if recommendation_type:
            query += " AND r.RECOMMENDATION_TYPE = %s"
            parameters.append(recommendation_type)

        if recommendation_status:
            query += " AND r.STATUS = %s"
            parameters.append(recommendation_status)

        if min_recommendation_score is not None:
            query += " AND r.RECOMMENDATION_SCORE >= %s"
            parameters.append(min_recommendation_score)

        query += """
            ORDER BY
                o.PRIORITY,
                o.WIN_PROBABILITY_PCT DESC,
                o.ESTIMATED_OPPORTUNITY_VALUE DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                opp_dict = {
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

                # Add recommendation data if available
                if has_rec_filters:
                    opp_dict.update({
                        "recommendation_id": row["RECOMMENDATION_ID"],
                        "recommendation_type": row["RECOMMENDATION_TYPE"],
                        "recommendation_score": row["RECOMMENDATION_SCORE"],
                        "rationale": row["RATIONALE"],
                        "expected_impact": row["EXPECTED_IMPACT"],
                        "recommended_timeframe": row["RECOMMENDED_TIMEFRAME"],
                        "recommendation_status": row["RECOMMENDATION_STATUS"],
                    })

                result.append(opp_dict)

            return result

        finally:
            cursor.close()


if __name__ == "__main__":
    repository = SnowflakeGTMRepository()

    # Old way: two separate calls
    # result1 = repository.search_gtm_opportunities(priority="High", limit=10)
    # result2 = repository.get_gtm_recommendations(
    #     partner_id="P123", recommendation_type="Expansion"
    # )

    # New way: one call with recommendations included
    result = repository.search_gtm_opportunities(
        priority="Critical",
        include_recommendations=True,
        recommendation_type="Joint Campaign",
        limit=10
    )

    for row in result:
        print(row)

    repository.close()