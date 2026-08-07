import os

from partner_generator import generate_partners
from capability_generator import generate_capabilities
from program_generator import generate_programs
from classification_generator import generate_classifications
from document_generator import generate_documents
from validate_data import validate_dataset

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

GENERATED_DIR = os.path.join(BASE_DIR, "generated")


def main():
    print("=" * 60)
    print("PARTNER DATASET GENERATION")
    print("=" * 60)

    os.makedirs(GENERATED_DIR, exist_ok=True)

    print("\n1. Generating partner master...")
    generate_partners(GENERATED_DIR)

    print("\n2. Generating capabilities...")
    generate_capabilities(GENERATED_DIR)

    print("\n3. Generating partner programs...")
    generate_programs(GENERATED_DIR)

    print("\n4. Generating classifications...")
    generate_classifications(GENERATED_DIR)

    print("\n5. Generating partner documents...")
    generate_documents(GENERATED_DIR)

    print("\n6. Validating generated dataset...")
    validate_dataset(GENERATED_DIR)

    print("\n" + "=" * 60)
    print("DATASET GENERATION COMPLETED")
    print("=" * 60)

    print(f"\nGenerated data location:")
    print(GENERATED_DIR)


if __name__ == "__main__":
    main()
