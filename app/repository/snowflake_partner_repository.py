import json
import os

import numpy as np
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

QUERY_LIMIT = 100

class SnowflakePartnerRepository:

    DOC_CHUNKS_TABLE = "PARTNER_DOC_CHUNKS"

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
        query = """
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
            FROM PARTNER_MASTER
            WHERE partner_id = %s
        """

        cursor = self.connection.cursor(snowflake.connector.DictCursor)

        try:
            cursor.execute(query, (partner_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_capabilities(self, partner_id):
        query = """
            SELECT
                partner_id,
                capability,
                proficiency_level,
                years_of_experience,
                certification_count
            FROM PARTNER_CAPABILITIES
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
        query = """
            SELECT
                partner_id,
                vendor,
                program_name,
                partner_tier,
                status,
                enrollment_date
            FROM PARTNER_PROGRAMS
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
        query = """
            SELECT
                partner_id,
                classification,
                primary_classification
            FROM PARTNER_CLASSIFICATIONS
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
        query = """
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
            FROM PARTNER_MASTER p
            LEFT JOIN PARTNER_CAPABILITIES c
                ON p.partner_id = c.partner_id
            LEFT JOIN PARTNER_PROGRAMS pr
                ON p.partner_id = pr.partner_id
            LEFT JOIN PARTNER_CLASSIFICATIONS cl
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

    def ensure_doc_chunks_table(self):
        query = f"""
            CREATE TABLE IF NOT EXISTS {self.DOC_CHUNKS_TABLE} (
                partner_id     VARCHAR(16),
                chunk_index    INTEGER,
                heading        VARCHAR(256),
                text           VARCHAR,
                embedding      ARRAY,
                PRIMARY KEY (partner_id, chunk_index)
            )
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        finally:
            cursor.close()

    def upsert_doc_chunks(self, chunks):
        self.ensure_doc_chunks_table()

        cursor = self.connection.cursor()
        try:
            for chunk in chunks:
                embedding_json = json.dumps(chunk.embedding)

                cursor.execute(
                    f"""
                    MERGE INTO {self.DOC_CHUNKS_TABLE} AS t
                    USING (SELECT %s AS partner_id, %s AS chunk_index) AS s
                    ON t.partner_id = s.partner_id AND t.chunk_index = s.chunk_index
                    WHEN MATCHED THEN UPDATE SET
                        heading = %s,
                        text = %s,
                        embedding = PARSE_JSON(%s)
                    WHEN NOT MATCHED THEN INSERT (
                        partner_id, chunk_index, heading, text, embedding
                    ) VALUES (%s, %s, %s, %s, PARSE_JSON(%s))
                    """,
                    (
                        chunk.partner_id,
                        chunk.chunk_index,
                        chunk.heading,
                        chunk.text,
                        embedding_json,
                        chunk.partner_id,
                        chunk.chunk_index,
                        chunk.heading,
                        chunk.text,
                        embedding_json,
                    ),
                )

            self.connection.commit()
        finally:
            cursor.close()

    def fetch_all_doc_chunks(self):
        cursor = self.connection.cursor(snowflake.connector.DictCursor)
        try:
            cursor.execute(
                f"""
                SELECT partner_id, chunk_index, heading, text, embedding
                FROM {self.DOC_CHUNKS_TABLE}
                """
            )
            rows = cursor.fetchall()

            return [
                {
                    "partner_id": row["PARTNER_ID"],
                    "chunk_index": row["CHUNK_INDEX"],
                    "heading": row["HEADING"],
                    "text": row["TEXT"],
                    "embedding": row["EMBEDDING"],
                }
                for row in rows
            ]
        finally:
            cursor.close()

    def search_doc_chunks(self, query_embedding, top_k=5, threshold=0.0):
        chunks = self.fetch_all_doc_chunks()

        if not chunks:
            return []

        from app.rag.vector_store import cosine_similarity

        vectors = [c["embedding"] for c in chunks]

        scores = cosine_similarity(query_embedding, vectors)

        ranked = sorted(
            zip(chunks, scores), key=lambda item: item[1], reverse=True
        )

        results = [
            {"chunk": c, "score": float(score)}
            for c, score in ranked
            if float(score) >= threshold
        ]

        return results[:top_k]

    def count_doc_chunks(self):
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {self.DOC_CHUNKS_TABLE}")
            return cursor.fetchone()[0]
        finally:
            cursor.close()
