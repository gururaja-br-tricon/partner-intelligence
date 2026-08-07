import os
import sys
import pandas as pd

EXPECTED_PARTNER_COUNT = 10

REQUIRED_FILES = [
    "partner_master.csv",
    "partner_capabilities.csv",
    "partner_programs.csv",
    "partner_classifications.csv",
]


def load_csv(generated_dir, filename):
    file_path = os.path.join(generated_dir, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing required file: {file_path}")

    return pd.read_csv(file_path)


def validate_partner_master(df):
    print("\nValidating partner_master.csv...")

    required_columns = [
        "partner_id",
        "partner_name",
        "status",
        "website",
        "founded_year",
        "employee_count",
        "annual_revenue",
        "industry",
        "headquarters_country",
        "headquarters_state",
        "headquarters_city",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"partner_master.csv missing columns: {missing_columns}")

    if len(df) != EXPECTED_PARTNER_COUNT:
        raise ValueError(f"Expected {EXPECTED_PARTNER_COUNT} partners, " f"found {len(df)}")

    if df["partner_id"].duplicated().any():
        duplicates = df[df["partner_id"].duplicated(keep=False)]["partner_id"].tolist()
        raise ValueError(f"Duplicate partner_id values: {duplicates}")

    if df["partner_name"].duplicated().any():
        duplicates = df[df["partner_name"].duplicated(keep=False)]["partner_name"].tolist()
        raise ValueError(f"Duplicate partner_name values: {duplicates}")

    if df["employee_count"].isnull().any():
        raise ValueError("partner_master contains missing employee_count values")

    if df["annual_revenue"].isnull().any():
        raise ValueError("partner_master contains missing annual_revenue values")

    print(f"  Partners: {len(df)}")
    print("  Partner IDs: OK")
    print("  Partner names: OK")
    print("  Required columns: OK")


def validate_foreign_keys(df, partner_ids, dataset_name):
    if "partner_id" not in df.columns:
        raise ValueError(f"{dataset_name} does not contain partner_id")

    invalid_ids = set(df["partner_id"].dropna()) - partner_ids

    if invalid_ids:
        raise ValueError(f"{dataset_name} contains invalid partner IDs: " f"{sorted(invalid_ids)}")

    if df["partner_id"].isnull().any():
        raise ValueError(f"{dataset_name} contains NULL partner_id values")

    print(f"  {dataset_name} foreign keys: OK")


def validate_capabilities(df, partner_ids):
    print("\nValidating partner_capabilities.csv...")

    required_columns = [
        "partner_id",
        "capability",
        "proficiency_level",
        "years_of_experience",
        "certification_count",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"partner_capabilities.csv missing columns: " f"{missing_columns}")

    validate_foreign_keys(df, partner_ids, "partner_capabilities")

    duplicates = df.duplicated(subset=["partner_id", "capability"])

    if duplicates.any():
        duplicate_rows = df[duplicates]
        raise ValueError("Duplicate partner/capability combinations found:\n" f"{duplicate_rows}")

    allowed_levels = {
        "Basic",
        "Intermediate",
        "Advanced",
        "Expert",
    }

    invalid_levels = set(df["proficiency_level"]) - allowed_levels

    if invalid_levels:
        raise ValueError(f"Invalid proficiency levels: {invalid_levels}")

    if (df["years_of_experience"] < 0).any():
        raise ValueError("Negative years_of_experience found")

    if (df["certification_count"] < 0).any():
        raise ValueError("Negative certification_count found")

    print(f"  Capability records: {len(df)}")
    print("  Capability relationships: OK")
    print("  Proficiency levels: OK")


def validate_programs(df, partner_ids):
    print("\nValidating partner_programs.csv...")

    required_columns = [
        "partner_id",
        "vendor",
        "program_name",
        "partner_tier",
        "status",
        "enrollment_date",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"partner_programs.csv missing columns: " f"{missing_columns}")

    validate_foreign_keys(df, partner_ids, "partner_programs")

    duplicates = df.duplicated(subset=["partner_id", "vendor", "program_name"])

    if duplicates.any():
        duplicate_rows = df[duplicates]

        raise ValueError("Duplicate partner/program combinations found:\n" f"{duplicate_rows}")

    if df["enrollment_date"].isnull().any():
        raise ValueError("Missing enrollment dates found")

    print(f"  Program records: {len(df)}")
    print("  Program relationships: OK")
    print("  Enrollment dates: OK")


def validate_classifications(df, partner_ids):
    print("\nValidating partner_classifications.csv...")

    required_columns = [
        "partner_id",
        "classification",
        "primary_classification",
    ]

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"partner_classifications.csv missing columns: " f"{missing_columns}")

    validate_foreign_keys(df, partner_ids, "partner_classifications")

    duplicates = df.duplicated(subset=["partner_id", "classification"])

    if duplicates.any():
        duplicate_rows = df[duplicates]

        raise ValueError("Duplicate partner/classification combinations found:\n" f"{duplicate_rows}")

    primary_counts = (df[df["primary_classification"] == True].groupby("partner_id").size())

    invalid_primary = primary_counts[primary_counts != 1]

    if not invalid_primary.empty:
        raise ValueError(
            "Every partner must have exactly one "
            "primary classification.\n"
            f"Invalid partners: {invalid_primary.to_dict()}"
        )

    print(f"  Classification records: {len(df)}")
    print("  Classification relationships: OK")
    print("  Primary classifications: OK")


def validate_documents(generated_dir, partner_ids):
    print("\nValidating partner documents...")

    documents_dir = os.path.join(generated_dir, "documents")

    if not os.path.exists(documents_dir):
        raise FileNotFoundError(
            f"Documents directory does not exist: " f"{documents_dir}"
        )

    pdf_files = [
        filename
        for filename in os.listdir(documents_dir)
        if filename.lower().endswith(".pdf")
    ]

    pdf_partner_ids = {os.path.splitext(filename)[0] for filename in pdf_files}

    missing_documents = partner_ids - pdf_partner_ids

    unexpected_documents = pdf_partner_ids - partner_ids

    if missing_documents:
        raise ValueError("Missing PDF documents for partners: " f"{sorted(missing_documents)}")

    if unexpected_documents:
        raise ValueError("PDFs found for unknown partners: " f"{sorted(unexpected_documents)}")

    if len(pdf_files) != len(partner_ids):
        raise ValueError(f"Expected {len(partner_ids)} PDFs, " f"found {len(pdf_files)}")

    print(f"  PDF documents: {len(pdf_files)}")
    print("  PDF partner IDs: OK")


def validate_business_relationships(partners, capabilities, programs, classifications):
    print("\nValidating business relationships...")

    partner_ids = set(partners["partner_id"])

    partners_without_capabilities = partner_ids - set(capabilities["partner_id"])

    if partners_without_capabilities:
        raise ValueError("Partners without capabilities: " f"{sorted(partners_without_capabilities)}")

    partners_without_programs = partner_ids - set(programs["partner_id"])

    if partners_without_programs:
        raise ValueError("Partners without programs: " f"{sorted(partners_without_programs)}")

    partners_without_classifications = partner_ids - set(classifications["partner_id"])

    if partners_without_classifications:
        raise ValueError(
            "Partners without classifications: "
            f"{sorted(partners_without_classifications)}"
        )

    print("  Every partner has capabilities: OK")
    print("  Every partner has programs: OK")
    print("  Every partner has classifications: OK")


def validate_expected_scenarios(partners, capabilities, programs, classifications):
    print("\nValidating demo scenarios...")

    merged = partners.merge(capabilities, on="partner_id")

    merged = merged.merge(programs, on="partner_id")

    merged = merged.merge(classifications, on="partner_id")

    scenario_1 = merged[
        (merged["headquarters_state"] == "Texas")
        & (merged["vendor"] == "Microsoft")
        & (merged["partner_tier"] == "Gold")
        & (merged["capability"] == "AI")
    ]

    if scenario_1.empty:
        raise ValueError("Demo scenario failed: " "Texas + Microsoft Gold + AI")

    print(
        "  Texas + Microsoft Gold + AI: "
        f"{scenario_1['partner_name'].nunique()} partners"
    )

    scenario_2 = merged[
        (merged["vendor"] == "AWS") & (merged["capability"] == "Cybersecurity")
    ]

    if scenario_2.empty:
        raise ValueError("Demo scenario failed: " "AWS + Cybersecurity")

    print("  AWS + Cybersecurity: " f"{scenario_2['partner_name'].nunique()} partners")

    scenario_3 = merged[
        (merged["vendor"] == "Microsoft")
        & (merged["capability"] == "AI")
        & (merged["proficiency_level"].isin(["Advanced", "Expert"]))
    ]

    if scenario_3.empty:
        raise ValueError("Demo scenario failed: " "Microsoft + Advanced/Expert AI")

    print(
        "  Microsoft + Advanced/Expert AI: "
        f"{scenario_3['partner_name'].nunique()} partners"
    )

    scenario_4 = merged[
        (merged["classification"] == "MSP") & (merged["capability"] == "Cybersecurity")
    ]

    if scenario_4.empty:
        raise ValueError("Demo scenario failed: " "MSP + Cybersecurity")

    print("  MSP + Cybersecurity: " f"{scenario_4['partner_name'].nunique()} partners")


def validate_dataset(generated_dir):
    print("=" * 60)
    print("PARTNER DATASET VALIDATION")
    print("=" * 60)

    partners = load_csv(generated_dir, "partner_master.csv")

    capabilities = load_csv(generated_dir, "partner_capabilities.csv")

    programs = load_csv(generated_dir, "partner_programs.csv")

    classifications = load_csv(generated_dir, "partner_classifications.csv")

    validate_partner_master(partners)

    partner_ids = set(partners["partner_id"])

    validate_capabilities(capabilities, partner_ids)

    validate_programs(programs, partner_ids)

    validate_classifications(classifications, partner_ids)

    validate_documents(generated_dir, partner_ids)

    validate_business_relationships(partners, capabilities, programs, classifications)

    validate_expected_scenarios(partners, capabilities, programs, classifications)

    print("\n" + "=" * 60)
    print("VALIDATION PASSED")
    print("=" * 60)


if __name__ == "__main__":
    generated_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "generated"
    )

    try:
        validate_dataset(generated_dir)
    except Exception as error:
        print("\n" + "=" * 60)
        print("VALIDATION FAILED")
        print("=" * 60)
        print(f"\nError: {error}")

        sys.exit(1)
