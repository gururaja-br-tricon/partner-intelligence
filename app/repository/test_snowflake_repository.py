from app.repository.snowflake_partner_repository import (
    SnowflakePartnerRepository
)


repository = SnowflakePartnerRepository()

try:
    # print("\n--- Partner Profile From Snowflake ---")

    # profile = repository.get_partner_profile("P001")

    # print(profile)
    
    
    print("\n--- Texas + Microsoft Gold + Expert AI + MSP ---")

    results = repository.search_partners(
        headquarters_state="Texas",
        capability="AI",
        proficiency_level="Expert",
        vendor="Microsoft",
        partner_tier="Gold",
        classification="MSP"
    )

    for result in results:
        print(result)

finally:
    repository.close()