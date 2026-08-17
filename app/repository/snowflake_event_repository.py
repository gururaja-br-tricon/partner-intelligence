import os

import snowflake.connector
from dotenv import load_dotenv

from app.repository.snowflake_partner_repository import SnowflakePartnerRepository

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


class SnowflakeEventRepository:

    def __init__(self):
        self.connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_EVENT_USER"),
            password=os.getenv("SNOWFLAKE_EVENT_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            role=os.getenv("SNOWFLAKE_EVENT_ROLE"),
        )

    def close(self):
        self.connection.close()

    def search_events(
        self,
        event_name=None,
        event_type=None,
        region=None,
        country=None,
        city=None,
        industry=None,
        market_name=None,
        technology=None,
        event_status=None,
        event_date=None,
        event_end_date=None,
        limit=100,
    ):
        query = f"""
            SELECT
                EVENT_ID,
                EVENT_NAME,
                EVENT_TYPE,
                EVENT_DATE,
                EVENT_END_DATE,
                REGION,
                COUNTRY,
                CITY,
                INDUSTRY,
                MARKET_NAME,
                TECHNOLOGY,
                EXPECTED_ATTENDEES,
                ENTERPRISE_ATTENDEE_PCT,
                EXECUTIVE_ATTENDEE_PCT,
                SPONSOR_COUNT,
                EVENT_RELEVANCE_SCORE,
                EVENT_STATUS
            FROM {EVENTS}
            WHERE 1 = 1
        """

        parameters = []

        if event_name:
            query += " AND EVENT_NAME = %s"
            parameters.append(event_name)

        if region:
            query += " AND REGION = %s"
            parameters.append(region)

        if industry:
            query += " AND INDUSTRY = %s"
            parameters.append(industry)

        if technology:
            query += " AND TECHNOLOGY = %s"
            parameters.append(technology)

        if event_status:
            query += " AND EVENT_STATUS = %s"
            parameters.append(event_status)

        if event_date:
            query += " AND EVENT_DATE >= %s"
            parameters.append(event_date)

        if event_end_date:
            query += " AND EVENT_END_DATE <= %s"
            parameters.append(event_end_date)

        if event_type:
            query += " AND EVENT_TYPE = %s"
            parameters.append(event_type)

        if market_name:
            query += " AND MARKET_NAME = %s"
            parameters.append(market_name)

        if country:
            query += " AND COUNTRY = %s"
            parameters.append(country)

        if city:
            query += " AND CITY = %s"
            parameters.append(city)

        query += """
            ORDER BY event_date
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "event_id": row["EVENT_ID"],
                    "event_name": row["EVENT_NAME"],
                    "event_type": row["EVENT_TYPE"],
                    "event_date": row["EVENT_DATE"],
                    "event_end_date": row["EVENT_END_DATE"],
                    "region": row["REGION"],
                    "country": row["COUNTRY"],
                    "city": row["CITY"],
                    "industry": row["INDUSTRY"],
                    "market_name": row["MARKET_NAME"],
                    "technology": row["TECHNOLOGY"],
                    "expected_attendees": row["EXPECTED_ATTENDEES"],
                    "enterprise_attendee_pct": row["ENTERPRISE_ATTENDEE_PCT"],
                    "executive_attendee_pct": row["EXECUTIVE_ATTENDEE_PCT"],
                    "sponsor_count": row["SPONSOR_COUNT"],
                    "event_relevance_score": row["EVENT_RELEVANCE_SCORE"],
                    "event_status": row["EVENT_STATUS"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def get_event_participants(
        self, event_id=None, partner_id=None, participation_type=None, limit=100
    ):
        query = f"""
            SELECT
                PARTICIPANT_ID,
                EVENT_ID,
                PARTNER_ID,
                PARTICIPATION_TYPE,
                BOOTH,
                MEETING_REQUESTS,
                QUALIFIED_LEADS,
                EVENT_ENGAGEMENT_SCORE
            FROM {EVENT_PARTICIPANTS}
            WHERE 1 = 1
        """

        parameters = []

        if event_id:
            query += " AND event_id = %s"
            parameters.append(event_id)

        if partner_id:
            query += " AND partner_id = %s"
            parameters.append(partner_id)

        if participation_type:
            query += " AND participation_type = %s"
            parameters.append(participation_type)

        query += """
            ORDER BY EVENT_ID, PARTNER_ID
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "participant_id": row["PARTICIPANT_ID"],
                    "event_id": row["EVENT_ID"],
                    "partner_id": row["PARTNER_ID"],
                    "participation_type": row["PARTICIPATION_TYPE"],
                    "booth": row["BOOTH"],
                    "meeting_requests": row["MEETING_REQUESTS"],
                    "qualified_leads": row["QUALIFIED_LEADS"],
                    "event_engagement_score": row["EVENT_ENGAGEMENT_SCORE"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def find_partner_matches(
        self,
        partner_id=None,
        market_id=None,
        region=None,
        industry=None,
        technology=None,
        min_match_score=None,
        match_status=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT
                MATCH_ID,
                PARTNER_ID,
                MARKET_ID,
                MARKET_NAME,
                REGION,
                INDUSTRY,
                TECHNOLOGY,
                CAPABILITY_FIT_SCORE,
                GEOGRAPHIC_FIT_SCORE,
                INDUSTRY_FIT_SCORE,
                GROWTH_MOMENTUM_SCORE,
                HEALTH_SCORE,
                OVERALL_MATCH_SCORE,
                RECOMMENDATION,
                MATCH_STATUS
            FROM {PARTNER_MATCHES}
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

        if min_match_score is not None:
            query += " AND OVERALL_MATCH_SCORE >= %s"
            parameters.append(min_match_score)

        if match_status:
            query += " AND MATCH_STATUS = %s"
            parameters.append(match_status)

        query += """
            ORDER BY OVERALL_MATCH_SCORE DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "match_id": row["MATCH_ID"],
                    "partner_id": row["PARTNER_ID"],
                    "market_id": row["MARKET_ID"],
                    "market_name": row["MARKET_NAME"],
                    "region": row["REGION"],
                    "industry": row["INDUSTRY"],
                    "technology": row["TECHNOLOGY"],
                    "capability_fit_score": row["CAPABILITY_FIT_SCORE"],
                    "geographic_fit_score": row["GEOGRAPHIC_FIT_SCORE"],
                    "industry_fit_score": row["INDUSTRY_FIT_SCORE"],
                    "growth_momentum_score": row["GROWTH_MOMENTUM_SCORE"],
                    "health_score": row["HEALTH_SCORE"],
                    "overall_match_score": row["OVERALL_MATCH_SCORE"],
                    "recommendation": row["RECOMMENDATION"],
                    "match_status": row["MATCH_STATUS"],
                }
                for row in rows
            ]

        finally:
            cursor.close()

    def explain_partner_match(
        self,
        match_id=None,
        partner_id=None,
        market_id=None,
    ):
        query = f"""
            SELECT
                MATCH_ID,
                PARTNER_ID,
                MARKET_ID,
                MARKET_NAME,
                REGION,
                INDUSTRY,
                TECHNOLOGY,
                CAPABILITY_FIT_SCORE,
                GEOGRAPHIC_FIT_SCORE,
                INDUSTRY_FIT_SCORE,
                GROWTH_MOMENTUM_SCORE,
                HEALTH_SCORE,
                OVERALL_MATCH_SCORE,
                RECOMMENDATION,
                MATCH_STATUS
            FROM {PARTNER_MATCHES}
            WHERE 1 = 1
        """

        parameters = []

        if match_id:
            query += " AND MATCH_ID = %s"
            parameters.append(match_id)

        if partner_id:
            query += " AND PARTNER_ID = %s"
            parameters.append(partner_id)

        if market_id:
            query += " AND MARKET_ID = %s"
            parameters.append(market_id)

        query += """
            ORDER BY OVERALL_MATCH_SCORE DESC
            LIMIT 1
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            row = cursor.fetchone()

            if not row:
                return None

            return {
                "match_id": row["MATCH_ID"],
                "partner_id": row["PARTNER_ID"],
                "market_id": row["MARKET_ID"],
                "market_name": row["MARKET_NAME"],
                "region": row["REGION"],
                "industry": row["INDUSTRY"],
                "technology": row["TECHNOLOGY"],
                "capability_fit_score": row["CAPABILITY_FIT_SCORE"],
                "geographic_fit_score": row["GEOGRAPHIC_FIT_SCORE"],
                "industry_fit_score": row["INDUSTRY_FIT_SCORE"],
                "growth_momentum_score": row["GROWTH_MOMENTUM_SCORE"],
                "health_score": row["HEALTH_SCORE"],
                "overall_match_score": row["OVERALL_MATCH_SCORE"],
                "recommendation": row["RECOMMENDATION"],
                "match_status": row["MATCH_STATUS"],
            }

        finally:
            cursor.close()


if __name__ == "__main__":
    import os

    print("EVENT USER:", repr(os.getenv("SNOWFLAKE_EVENT_USER")))
    print("EVENT PASSWORD:", bool(os.getenv("SNOWFLAKE_EVENT_PASSWORD")))
    print("ACCOUNT:", repr(os.getenv("SNOWFLAKE_ACCOUNT")))

    repository = SnowflakeEventRepository()

    result = repository.search_events(
        limit=10
    )

    for row in result:
        print(row)

    repository.close()
