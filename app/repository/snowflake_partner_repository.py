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


class SnowflakePartnerRepository:

    def __init__(self):
        self.connection = snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_PARTNER_USER"),
            password=os.getenv("SNOWFLAKE_PARTNER_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            role=os.getenv("SNOWFLAKE_PARTNER_ROLE"),
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

    # ============================================================================
    # CONSOLIDATED METHOD: search_partners now includes performance filters
    # REMOVES: search_partner_growth (old separate method)
    # ============================================================================
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
        # NEW: Performance/growth filters (from old search_partner_growth)
        min_revenue_growth_pct=None,
        min_pipeline_growth_pct=None,
        min_health_score=None,
        performance_status=None,
        performance_year=None,
        limit=QUERY_LIMIT,
    ):
        """
        Search partners with optional performance filtering.
        
        This method consolidates search_partners + search_partner_growth.
        If performance filters are provided, it joins PARTNER_PERFORMANCE.
        """
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
        """
        
        # Add performance columns to SELECT if performance filters are requested
        has_perf_filters = any([
            min_revenue_growth_pct is not None,
            min_pipeline_growth_pct is not None,
            min_health_score is not None,
            performance_status is not None,
            performance_year is not None,
        ])
        
        if has_perf_filters:
            query += """
                , perf.performance_year,
                perf.revenue,
                perf.revenue_growth_pct,
                perf.pipeline_value,
                perf.pipeline_growth_pct,
                perf.partner_health_score,
                perf.performance_status
            """
        
        query += f"""
            FROM {PARTNER_MASTER} p
            LEFT JOIN {PARTNER_CAPABILITIES} c
                ON p.partner_id = c.partner_id
            LEFT JOIN {PARTNER_PROGRAMS} pr
                ON p.partner_id = pr.partner_id
            LEFT JOIN {PARTNER_CLASSIFICATIONS} cl
                ON p.partner_id = cl.partner_id
        """
        
        # Add performance join only if needed
        if has_perf_filters:
            query += f"""
            LEFT JOIN {PARTNER_PERFORMANCE} perf
                ON p.partner_id = perf.partner_id
            """
        
        query += " WHERE 1 = 1"

        parameters = []

        # Original filters
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

        # NEW: Performance filters
        if min_revenue_growth_pct is not None:
            query += " AND perf.revenue_growth_pct >= %s"
            parameters.append(min_revenue_growth_pct)

        if min_pipeline_growth_pct is not None:
            query += " AND perf.pipeline_growth_pct >= %s"
            parameters.append(min_pipeline_growth_pct)

        if min_health_score is not None:
            query += " AND perf.partner_health_score >= %s"
            parameters.append(min_health_score)

        if performance_status:
            query += " AND perf.performance_status = %s"
            parameters.append(performance_status)

        if performance_year is not None:
            query += " AND perf.performance_year = %s"
            parameters.append(performance_year)

        query += """
            ORDER BY
        """
        
        # Smart ordering: if performance filters present, prioritize performance metrics
        if has_perf_filters:
            query += """
                perf.revenue_growth_pct DESC,
                perf.pipeline_growth_pct DESC,
                perf.partner_health_score DESC
            """
        else:
            query += " p.partner_name"

        if limit:
            query += " LIMIT %s"
            parameters.append(limit)

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                partner_dict = {
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
                
                # Add performance data if available
                if has_perf_filters:
                    partner_dict.update({
                        "performance_year": row["PERFORMANCE_YEAR"],
                        "revenue": row["REVENUE"],
                        "revenue_growth_pct": row["REVENUE_GROWTH_PCT"],
                        "pipeline_value": row["PIPELINE_VALUE"],
                        "pipeline_growth_pct": row["PIPELINE_GROWTH_PCT"],
                        "partner_health_score": row["PARTNER_HEALTH_SCORE"],
                        "performance_status": row["PERFORMANCE_STATUS"],
                    })
                
                result.append(partner_dict)
            
            return result
        finally:
            cursor.close()

    # ============================================================================
    # KEEP: get_partner_performance (used by get_partner_profile for full history)
    # ============================================================================
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


if __name__ == "__main__":
    repository = SnowflakePartnerRepository()

    # Old way: two separate calls
    # result1 = repository.search_partners(industry="tech")
    # result2 = repository.search_partner_growth(min_revenue_growth_pct=10)

    # New way: one call with all filters
    result = repository.search_partners(
        industry="Enterprise Software",
        min_revenue_growth_pct=10,
        min_pipeline_growth_pct=5,
        limit=10
    )

    for row in result:
        print(row)

    repository.close()