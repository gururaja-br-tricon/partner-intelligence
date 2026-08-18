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

    # ============================================================================
    # CONSOLIDATED METHOD: search_events now includes participant data
    # REMOVES: get_event_participants (old separate method)
    # ============================================================================
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
        # NEW: Participant filters (from old get_event_participants)
        participant_type=None,
        include_participants=False,  # Flag to include participant details
        limit=100,
    ):
        """
        Search events with optional participant data.
        
        This method consolidates search_events + get_event_participants.
        If include_participants=True or participant_type is specified,
        it joins EVENT_PARTICIPANTS and returns attendance details.
        """
        
        has_participant_filters = any([
            participant_type is not None,
            include_participants is True,
        ])

        query = f"""
            SELECT
                e.EVENT_ID,
                e.EVENT_NAME,
                e.EVENT_TYPE,
                e.EVENT_DATE,
                e.EVENT_END_DATE,
                e.REGION,
                e.COUNTRY,
                e.CITY,
                e.INDUSTRY,
                e.MARKET_NAME,
                e.TECHNOLOGY,
                e.EXPECTED_ATTENDEES,
                e.ENTERPRISE_ATTENDEE_PCT,
                e.EXECUTIVE_ATTENDEE_PCT,
                e.SPONSOR_COUNT,
                e.EVENT_RELEVANCE_SCORE,
                e.EVENT_STATUS
        """

        # Add participant columns if requested
        if has_participant_filters:
            query += """
                , ep.PARTICIPANT_ID,
                ep.PARTNER_ID,
                ep.PARTICIPATION_TYPE,
                ep.BOOTH,
                ep.MEETING_REQUESTS,
                ep.QUALIFIED_LEADS,
                ep.EVENT_ENGAGEMENT_SCORE
            """

        query += f"""
            FROM {EVENTS} e
        """

        # Add participant join if needed
        if has_participant_filters:
            query += f"""
            LEFT JOIN {EVENT_PARTICIPANTS} ep
                ON e.EVENT_ID = ep.EVENT_ID
            """

        query += " WHERE 1 = 1"

        parameters = []

        # Event filters
        if event_name:
            query += " AND e.EVENT_NAME = %s"
            parameters.append(event_name)

        if region:
            query += " AND e.REGION = %s"
            parameters.append(region)

        if industry:
            query += " AND e.INDUSTRY = %s"
            parameters.append(industry)

        if technology:
            query += " AND e.TECHNOLOGY = %s"
            parameters.append(technology)

        if event_status:
            query += " AND e.EVENT_STATUS = %s"
            parameters.append(event_status)

        if event_date:
            query += " AND e.EVENT_DATE >= %s"
            parameters.append(event_date)

        if event_end_date:
            query += " AND e.EVENT_END_DATE <= %s"
            parameters.append(event_end_date)

        if event_type:
            query += " AND e.EVENT_TYPE = %s"
            parameters.append(event_type)

        if market_name:
            query += " AND e.MARKET_NAME = %s"
            parameters.append(market_name)

        if country:
            query += " AND e.COUNTRY = %s"
            parameters.append(country)

        if city:
            query += " AND e.CITY = %s"
            parameters.append(city)

        # NEW: Participant filters
        if participant_type:
            query += " AND ep.PARTICIPATION_TYPE = %s"
            parameters.append(participant_type)

        query += " ORDER BY e.event_date"

        if limit:
            query += " LIMIT %s"
            parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                event_dict = {
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

                # Add participant data if available
                if has_participant_filters:
                    event_dict.update({
                        "participant_id": row["PARTICIPANT_ID"],
                        "partner_id": row["PARTNER_ID"],
                        "participation_type": row["PARTICIPATION_TYPE"],
                        "booth": row["BOOTH"],
                        "meeting_requests": row["MEETING_REQUESTS"],
                        "qualified_leads": row["QUALIFIED_LEADS"],
                        "event_engagement_score": row["EVENT_ENGAGEMENT_SCORE"],
                    })

                result.append(event_dict)

            return result

        finally:
            cursor.close()

    # ============================================================================
    # CONSOLIDATED METHOD: find_partner_matches now returns all details
    # REMOVES: explain_partner_match (old separate method - redundant)
    # ============================================================================
    def find_partner_matches(
        self,
        partner_id=None,
        market_id=None,
        region=None,
        industry=None,
        technology=None,
        min_match_score=None,
        match_status=None,
        match_id=None,  # Can query by specific match too
        limit=QUERY_LIMIT,
    ):
        """
        Find partner-to-market matches with all scoring details.
        
        This method consolidates find_partner_matches + explain_partner_match.
        The explain_partner_match was just filtering to 1 record - 
        the LLM can do that from the full result set.
        """
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


if __name__ == "__main__":
    repository = SnowflakeEventRepository()

    # Old way: two separate calls for event + participants
    # result1 = repository.search_events(event_type="Conference", limit=10)
    # result2 = repository.get_event_participants(event_id="EV123", limit=100)

    # New way: one call with participants included
    result = repository.search_events(
        event_type="Conference",
        include_participants=True,
        limit=10
    )

    for row in result:
        print(row)

    # Old way: two separate calls for match explanation
    # result1 = repository.find_partner_matches(partner_id="P123", limit=10)
    # result2 = repository.explain_partner_match(match_id="M456")

    # New way: one call returns all details
    matches = repository.find_partner_matches(
        partner_id="P123",
        limit=10
    )

    for match in matches:
        print(match)

    repository.close()