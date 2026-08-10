import os

from partner_repository import PartnerRepository

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "generated"
)


def main():
    repository = PartnerRepository(DATA_DIR)

    print("\n--- Partner Profile ---")

    profile = repository.get_partner_profile("P001")

    print(profile)


if __name__ == "__main__":
    main()
