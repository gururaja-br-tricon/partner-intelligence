import os

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

QUERY_LIMIT = 100

DATABASE = "PARTNER_INTELLIGENCE_DB"
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


class SnowflakePartnerRepository:

    def __init__(self):
        self.connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )

    def close(self):
        self.connection.close()

    def get_partner(self, partner_id):
        query = f"""
            SELECT
                partner_id,
                partner_name,
                status,
                website,
                founded_year,
                employee_count,
                annual_revenue,
                industry,
                headquarters_country,
                headquarters_state,
                headquarters_city
            FROM {PARTNER_MASTER}
            WHERE partner_id = %s
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_capabilities(self, partner_id):
        query = f"""
            SELECT
                partner_id,
                capability,
                proficiency_level,
                years_of_experience,
                certification_count
            FROM {PARTNER_CAPABILITIES}
            WHERE partner_id = %s
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "capability": row["CAPABILITY"],
                    "proficiency_level": row["PROFICIENCY_LEVEL"],
                    "years_of_experience": row["YEARS_OF_EXPERIENCE"],
                    "certification_count": row["CERTIFICATION_COUNT"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def get_programs(self, partner_id):
        query = f"""
            SELECT
                partner_id,
                vendor,
                program_name,
                partner_tier,
                status,
                enrollment_date
            FROM {PARTNER_PROGRAMS}
            WHERE partner_id = %s
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "vendor": row["VENDOR"],
                    "program_name": row["PROGRAM_NAME"],
                    "partner_tier": row["PARTNER_TIER"],
                    "status": row["STATUS"],
                    "enrollment_date": str(row["ENROLLMENT_DATE"]),
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def get_classifications(self, partner_id):
        query = f"""
            SELECT
                partner_id,
                classification,
                primary_classification
            FROM {PARTNER_CLASSIFICATIONS}
            WHERE partner_id = %s
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "classification": row["CLASSIFICATION"],
                    "primary_classification": row["PRIMARY_CLASSIFICATION"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def get_partner_profile(self, partner_id):
        partner = self.get_partner(partner_id)

        if not partner:
            return None

        partner = {
            "partner_id": partner["PARTNER_ID"],
            "partner_name": partner["PARTNER_NAME"],
            "status": partner["STATUS"],
            "website": partner["WEBSITE"],
            "founded_year": partner["FOUNDED_YEAR"],
            "employee_count": partner["EMPLOYEE_COUNT"],
            "annual_revenue": partner["ANNUAL_REVENUE"],
            "industry": partner["INDUSTRY"],
            "headquarters_country": partner["HEADQUARTERS_COUNTRY"],
            "headquarters_state": partner["HEADQUARTERS_STATE"],
            "headquarters_city": partner["HEADQUARTERS_CITY"],
        }

        return {
            "partner": partner,
            "capabilities": self.get_capabilities(partner_id),
            "programs": self.get_programs(partner_id),
            "classifications": self.get_classifications(partner_id),
        }

    def search_partners(
        self,
        headquarters_state=None,
        headquarters_country=None,
        industry=None,
        status=None,
        capability=None,
        proficiency_level=None,
        vendor=None,
        program_name=None,
        partner_tier=None,
        classification=None,
    ):
        query = f"""
            SELECT DISTINCT
                p.partner_id,
                p.partner_name,
                p.status,
                p.website,
                p.founded_year,
                p.employee_count,
                p.annual_revenue,
                p.industry,
                p.headquarters_country,
                p.headquarters_state,
                p.headquarters_city
            FROM {PARTNER_MASTER} p
            LEFT JOIN {PARTNER_CAPABILITIES} c
                ON p.partner_id = c.partner_id
            LEFT JOIN {PARTNER_PROGRAMS} pr
                ON p.partner_id = pr.partner_id
            LEFT JOIN {PARTNER_CLASSIFICATIONS} cl
                ON p.partner_id = cl.partner_id
            WHERE 1 = 1
        """

        parameters = []

        if headquarters_state:
            query += " AND p.headquarters_state = %s"
            parameters.append(headquarters_state)

        if headquarters_country:
            query += " AND p.headquarters_country = %s"
            parameters.append(headquarters_country)

        if industry:
            query += " AND p.industry = %s"
            parameters.append(industry)

        if status:
            query += " AND p.status = %s"
            parameters.append(status)

        if capability:
            query += " AND c.capability = %s"
            parameters.append(capability)

        if proficiency_level:
            query += " AND c.proficiency_level = %s"
            parameters.append(proficiency_level)

        if vendor:
            query += " AND pr.vendor = %s"
            parameters.append(vendor)

        if program_name:
            query += " AND pr.program_name = %s"
            parameters.append(program_name)

        if partner_tier:
            query += " AND pr.partner_tier = %s"
            parameters.append(partner_tier)

        if classification:
            query += " AND cl.classification = %s"
            parameters.append(classification)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "partner_name": row["PARTNER_NAME"],
                    "status": row["STATUS"],
                    "website": row["WEBSITE"],
                    "founded_year": row["FOUNDED_YEAR"],
                    "employee_count": row["EMPLOYEE_COUNT"],
                    "annual_revenue": row["ANNUAL_REVENUE"],
                    "industry": row["INDUSTRY"],
                    "headquarters_country": row["HEADQUARTERS_COUNTRY"],
                    "headquarters_state": row["HEADQUARTERS_STATE"],
                    "headquarters_city": row["HEADQUARTERS_CITY"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def get_partner_performance(self, partner_id):
        query = f"""
            SELECT
                performance_id,
                partner_id,
                performance_year,
                revenue,
                revenue_growth_pct,
                employee_count,
                employee_growth_pct,
                customer_count,
                new_customer_count,
                churned_customer_count,
                retention_rate_pct,
                pipeline_value,
                pipeline_growth_pct,
                opportunities_created,
                opportunities_won,
                opportunities_lost,
                win_rate_pct,
                average_deal_size,
                capability_growth_count,
                strategic_investment_amount,
                partner_health_score,
                performance_status
            FROM {PARTNER_PERFORMANCE}
            WHERE partner_id = %s
            ORDER BY performance_year
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            rows = cursor.fetchall()

            return [
                {
                    "performance_id": row["PERFORMANCE_ID"],
                    "partner_id": row["PARTNER_ID"],
                    "performance_year": row["PERFORMANCE_YEAR"],
                    "revenue": row["REVENUE"],
                    "revenue_growth_pct": row["REVENUE_GROWTH_PCT"],
                    "employee_count": row["EMPLOYEE_COUNT"],
                    "employee_growth_pct": row["EMPLOYEE_GROWTH_PCT"],
                    "customer_count": row["CUSTOMER_COUNT"],
                    "new_customer_count": row["NEW_CUSTOMER_COUNT"],
                    "churned_customer_count": row["CHURNED_CUSTOMER_COUNT"],
                    "retention_rate_pct": row["RETENTION_RATE_PCT"],
                    "pipeline_value": row["PIPELINE_VALUE"],
                    "pipeline_growth_pct": row["PIPELINE_GROWTH_PCT"],
                    "opportunities_created": row["OPPORTUNITIES_CREATED"],
                    "opportunities_won": row["OPPORTUNITIES_WON"],
                    "opportunities_lost": row["OPPORTUNITIES_LOST"],
                    "win_rate_pct": row["WIN_RATE_PCT"],
                    "average_deal_size": row["AVERAGE_DEAL_SIZE"],
                    "capability_growth_count": row["CAPABILITY_GROWTH_COUNT"],
                    "strategic_investment_amount": row["STRATEGIC_INVESTMENT_AMOUNT"],
                    "partner_health_score": row["PARTNER_HEALTH_SCORE"],
                    "performance_status": row["PERFORMANCE_STATUS"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def search_partner_growth(
        self,
        min_revenue_growth_pct=None,
        min_pipeline_growth_pct=None,
        min_health_score=None,
        performance_status=None,
        performance_year=None,
        limit=QUERY_LIMIT,
    ):
        query = f"""
            SELECT
                partner_id,
                performance_year,
                revenue,
                revenue_growth_pct,
                employee_count,
                employee_growth_pct,
                customer_count,
                retention_rate_pct,
                pipeline_value,
                pipeline_growth_pct,
                opportunities_created,
                opportunities_won,
                opportunities_lost,
                win_rate_pct,
                partner_health_score,
                performance_status
            FROM {PARTNER_PERFORMANCE}
            WHERE 1 = 1
        """

        parameters = []

        if min_revenue_growth_pct is not None:
            query += " AND revenue_growth_pct >= %s"
            parameters.append(min_revenue_growth_pct)

        if min_pipeline_growth_pct is not None:
            query += " AND pipeline_growth_pct >= %s"
            parameters.append(min_pipeline_growth_pct)

        if min_health_score is not None:
            query += " AND partner_health_score >= %s"
            parameters.append(min_health_score)

        if performance_status:
            query += " AND performance_status = %s"
            parameters.append(performance_status)

        if performance_year is not None:
            query += " AND performance_year = %s"
            parameters.append(performance_year)

        query += """
            ORDER BY
                revenue_growth_pct DESC,
                pipeline_growth_pct DESC,
                partner_health_score DESC
            LIMIT %s
        """

        parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "performance_year": row["PERFORMANCE_YEAR"],
                    "revenue": row["REVENUE"],
                    "revenue_growth_pct": row["REVENUE_GROWTH_PCT"],
                    "employee_count": row["EMPLOYEE_COUNT"],
                    "employee_growth_pct": row["EMPLOYEE_GROWTH_PCT"],
                    "customer_count": row["CUSTOMER_COUNT"],
                    "retention_rate_pct": row["RETENTION_RATE_PCT"],
                    "pipeline_value": row["PIPELINE_VALUE"],
                    "pipeline_growth_pct": row["PIPELINE_GROWTH_PCT"],
                    "opportunities_created": row["OPPORTUNITIES_CREATED"],
                    "opportunities_won": row["OPPORTUNITIES_WON"],
                    "opportunities_lost": row["OPPORTUNITIES_LOST"],
                    "win_rate_pct": row["WIN_RATE_PCT"],
                    "partner_health_score": row["PARTNER_HEALTH_SCORE"],
                    "performance_status": row["PERFORMANCE_STATUS"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

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
    repository = SnowflakePartnerRepository()

    result = repository.search_partner_growth(
        min_revenue_growth_pct=10,
        performance_year=2026,
    )

    for row in result:
        print(row)

    repository.close()
