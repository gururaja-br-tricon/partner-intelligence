import os
import pandas as pd

PARTNER_CLASSIFICATIONS = {
    "P001": [
        ("MSP", True),
        ("System Integrator", False),
    ],
    "P002": [
        ("Cloud Service Provider", True),
        ("Managed Service Provider", False),
    ],
    "P003": [
        ("System Integrator", True),
        ("IT Consulting", False),
    ],
    "P004": [
        ("MSP", True),
        ("Value Added Reseller", False),
    ],
    "P005": [
        ("System Integrator", True),
        ("IT Consulting", False),
    ],
    "P006": [
        ("Value Added Reseller", True),
        ("System Integrator", False),
    ],
    "P007": [
        ("MSP", True),
        ("Cloud Service Provider", False),
    ],
    "P008": [
        ("System Integrator", True),
        ("Data & Analytics Specialist", False),
    ],
    "P009": [
        ("Value Added Reseller", True),
        ("IT Infrastructure Provider", False),
    ],
    "P010": [
        ("MSP", True),
        ("Cybersecurity Specialist", False),
    ],
}


def generate_classifications(output_dir):
    records = []

    for partner_id, classifications in PARTNER_CLASSIFICATIONS.items():
        for classification in classifications:
            records.append(
                {
                    "partner_id": partner_id,
                    "classification": classification[0],
                    "primary_classification": classification[1],
                }
            )

    df = pd.DataFrame(records)

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "partner_classifications.csv")

    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} classification records")
    print(f"Output: {output_file}")

    return df
