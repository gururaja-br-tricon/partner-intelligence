import os
import pandas as pd

PARTNER_CAPABILITIES = {
    "P001": [
        ("AI", "Expert", 8, 18),
        ("Cybersecurity", "Advanced", 7, 14),
        ("Cloud", "Expert", 9, 20),
        ("DevOps", "Advanced", 6, 11),
        ("Application Modernization", "Advanced", 6, 9),
    ],
    "P002": [
        ("Cloud", "Expert", 10, 22),
        ("AI", "Advanced", 6, 12),
        ("DevOps", "Expert", 8, 16),
        ("Application Modernization", "Advanced", 7, 13),
    ],
    "P003": [
        ("AI", "Expert", 9, 25),
        ("Data & Analytics", "Expert", 11, 28),
        ("Cloud", "Advanced", 8, 19),
        ("Digital Transformation", "Expert", 12, 30),
        ("Application Modernization", "Expert", 10, 21),
    ],
    "P004": [
        ("Cybersecurity", "Expert", 9, 20),
        ("Managed Services", "Expert", 12, 17),
        ("Cloud", "Advanced", 7, 13),
        ("Networking", "Advanced", 8, 15),
    ],
    "P005": [
        ("AI", "Advanced", 5, 10),
        ("Cloud", "Advanced", 6, 14),
        ("Data & Analytics", "Advanced", 7, 12),
        ("Digital Transformation", "Expert", 8, 18),
        ("DevOps", "Advanced", 5, 9),
    ],
    "P006": [
        ("Networking", "Expert", 15, 24),
        ("Infrastructure", "Expert", 14, 21),
        ("Cybersecurity", "Advanced", 8, 13),
        ("Cloud", "Advanced", 7, 11),
    ],
    "P007": [
        ("Managed Services", "Expert", 13, 19),
        ("Cloud", "Expert", 10, 17),
        ("Cybersecurity", "Advanced", 8, 14),
        ("Infrastructure", "Advanced", 9, 12),
        ("DevOps", "Advanced", 7, 10),
    ],
    "P008": [
        ("AI", "Expert", 8, 16),
        ("Data & Analytics", "Expert", 10, 23),
        ("Cloud", "Advanced", 7, 15),
        ("Digital Transformation", "Advanced", 6, 11),
    ],
    "P009": [
        ("Infrastructure", "Advanced", 10, 15),
        ("Networking", "Advanced", 9, 13),
        ("Cloud", "Advanced", 6, 10),
        ("Cybersecurity", "Advanced", 7, 12),
    ],
    "P010": [
        ("Cybersecurity", "Expert", 8, 22),
        ("Cloud", "Advanced", 6, 13),
        ("DevOps", "Advanced", 5, 9),
        ("Application Modernization", "Advanced", 5, 8),
    ],
}


def generate_capabilities(output_dir):
    records = []

    for partner_id, capabilities in PARTNER_CAPABILITIES.items():
        for capability in capabilities:
            records.append(
                {
                    "partner_id": partner_id,
                    "capability": capability[0],
                    "proficiency_level": capability[1],
                    "years_of_experience": capability[2],
                    "certification_count": capability[3],
                }
            )

    df = pd.DataFrame(records)

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "partner_capabilities.csv")

    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} capability records")
    print(f"Output: {output_file}")

    return df
