import os
import pandas as pd

PARTNER_PROGRAMS = {
    "P001": [
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2021-04-15"),
        ("AWS", "AWS Partner Network", "Advanced", "Active", "2020-08-20"),
        ("Cisco", "Cisco Partner Program", "Premier", "Active", "2022-01-10"),
    ],
    "P002": [
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2022-03-18"),
        ("AWS", "AWS Partner Network", "Advanced", "Active", "2021-06-12"),
    ],
    "P003": [
        ("Microsoft", "Solutions Partner", "Platinum", "Active", "2019-05-21"),
        ("AWS", "AWS Partner Network", "Advanced", "Active", "2020-02-14"),
        (
            "Google Cloud",
            "Google Cloud Partner Advantage",
            "Premier",
            "Active",
            "2021-11-08",
        ),
    ],
    "P004": [
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2020-07-19"),
        ("Cisco", "Cisco Partner Program", "Gold", "Active", "2021-09-05"),
    ],
    "P005": [
        ("Microsoft", "Solutions Partner", "Silver", "Active", "2022-01-17"),
        ("AWS", "AWS Partner Network", "Select", "Active", "2022-08-11"),
        (
            "Google Cloud",
            "Google Cloud Partner Advantage",
            "Partner",
            "Active",
            "2023-02-06",
        ),
    ],
    "P006": [
        ("Cisco", "Cisco Partner Program", "Premier", "Active", "2018-06-12"),
        ("Microsoft", "Solutions Partner", "Silver", "Active", "2021-03-22"),
    ],
    "P007": [
        ("AWS", "AWS Partner Network", "Advanced", "Active", "2019-09-18"),
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2020-04-27"),
        ("Cisco", "Cisco Partner Program", "Premier", "Active", "2021-10-14"),
    ],
    "P008": [
        ("AWS", "AWS Partner Network", "Advanced", "Active", "2020-05-09"),
        (
            "Google Cloud",
            "Google Cloud Partner Advantage",
            "Premier",
            "Active",
            "2021-07-16",
        ),
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2022-02-25"),
    ],
    "P009": [
        ("Microsoft", "Solutions Partner", "Silver", "Active", "2021-08-13"),
        ("Cisco", "Cisco Partner Program", "Gold", "Active", "2022-04-29"),
    ],
    "P010": [
        ("Microsoft", "Solutions Partner", "Gold", "Active", "2020-11-06"),
        ("AWS", "AWS Partner Network", "Select", "Active", "2022-05-18"),
    ],
}


def generate_programs(output_dir):
    records = []

    for partner_id, programs in PARTNER_PROGRAMS.items():
        for program in programs:
            records.append(
                {
                    "partner_id": partner_id,
                    "vendor": program[0],
                    "program_name": program[1],
                    "partner_tier": program[2],
                    "status": program[3],
                    "enrollment_date": program[4],
                }
            )

    df = pd.DataFrame(records)

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "partner_programs.csv")

    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} program records")
    print(f"Output: {output_file}")

    return df
