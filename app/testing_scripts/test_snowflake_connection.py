import os

import snowflake.connector
from dotenv import load_dotenv


load_dotenv()


connection = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)

cursor = connection.cursor()

try:
    cursor.execute("SELECT CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
    result = cursor.fetchone()

    print("Snowflake connection successful")
    print(f"User: {result[0]}")
    print(f"Database: {result[1]}")
    print(f"Schema: {result[2]}")
finally:
    cursor.close()
    connection.close()