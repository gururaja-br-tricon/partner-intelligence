import os
import pandas as pd

PARTNERS = [
    {
        "partner_id": "P001",
        "partner_name": "Nexora Technologies",
        "status": "Active",
        "website": "https://www.nexoratechnologies.com",
        "founded_year": 2008,
        "employee_count": 850,
        "annual_revenue": 180_000_000,
        "industry": "Information Technology",
        "headquarters_country": "USA",
        "headquarters_state": "Texas",
        "headquarters_city": "Austin",
    },
    {
        "partner_id": "P002",
        "partner_name": "CloudBridge Solutions",
        "status": "Active",
        "website": "https://www.cloudbridgesolutions.com",
        "founded_year": 2012,
        "employee_count": 420,
        "annual_revenue": 95_000_000,
        "industry": "Cloud Services",
        "headquarters_country": "USA",
        "headquarters_state": "California",
        "headquarters_city": "San Francisco",
    },
    {
        "partner_id": "P003",
        "partner_name": "Vertex Digital Systems",
        "status": "Active",
        "website": "https://www.vertexdigitalsystems.com",
        "founded_year": 2005,
        "employee_count": 1200,
        "annual_revenue": 320_000_000,
        "industry": "Digital Transformation",
        "headquarters_country": "Germany",
        "headquarters_state": "Bavaria",
        "headquarters_city": "Munich",
    },
    {
        "partner_id": "P004",
        "partner_name": "BluePeak IT Services",
        "status": "Active",
        "website": "https://www.bluepeakitservices.com",
        "founded_year": 2010,
        "employee_count": 310,
        "annual_revenue": 65_000_000,
        "industry": "Managed Services",
        "headquarters_country": "USA",
        "headquarters_state": "Texas",
        "headquarters_city": "Dallas",
    },
    {
        "partner_id": "P005",
        "partner_name": "ApexSphere Consulting",
        "status": "Active",
        "website": "https://www.apexsphereconsulting.com",
        "founded_year": 2015,
        "employee_count": 275,
        "annual_revenue": 48_000_000,
        "industry": "IT Consulting",
        "headquarters_country": "India",
        "headquarters_state": "Karnataka",
        "headquarters_city": "Bangalore",
    },
    {
        "partner_id": "P006",
        "partner_name": "Crestview Technology Group",
        "status": "Active",
        "website": "https://www.crestviewtechnology.com",
        "founded_year": 2003,
        "employee_count": 680,
        "annual_revenue": 145_000_000,
        "industry": "Networking",
        "headquarters_country": "UK",
        "headquarters_state": "England",
        "headquarters_city": "London",
    },
    {
        "partner_id": "P007",
        "partner_name": "NorthStar Managed Services",
        "status": "Active",
        "website": "https://www.northstarmanagedservices.com",
        "founded_year": 2007,
        "employee_count": 540,
        "annual_revenue": 125_000_000,
        "industry": "Managed Services",
        "headquarters_country": "Canada",
        "headquarters_state": "Ontario",
        "headquarters_city": "Toronto",
    },
    {
        "partner_id": "P008",
        "partner_name": "QuantumEdge Solutions",
        "status": "Active",
        "website": "https://www.quantumedgesolutions.com",
        "founded_year": 2011,
        "employee_count": 390,
        "annual_revenue": 82_000_000,
        "industry": "Data & Analytics",
        "headquarters_country": "Australia",
        "headquarters_state": "New South Wales",
        "headquarters_city": "Sydney",
    },
    {
        "partner_id": "P009",
        "partner_name": "Silverline Systems",
        "status": "Active",
        "website": "https://www.silverlinesystems.com",
        "founded_year": 2006,
        "employee_count": 450,
        "annual_revenue": 105_000_000,
        "industry": "Enterprise Software",
        "headquarters_country": "India",
        "headquarters_state": "Maharashtra",
        "headquarters_city": "Mumbai",
    },
    {
        "partner_id": "P010",
        "partner_name": "BrightPath Digital",
        "status": "Active",
        "website": "https://www.brightpathdigital.com",
        "founded_year": 2014,
        "employee_count": 230,
        "annual_revenue": 42_000_000,
        "industry": "Cybersecurity",
        "headquarters_country": "Germany",
        "headquarters_state": "Berlin",
        "headquarters_city": "Berlin",
    },
]


def generate_partners(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    df = pd.DataFrame(PARTNERS)

    output_file = os.path.join(output_dir, "partner_master.csv")

    df.to_csv(output_file, index=False)

    print(f"Generated {len(df)} partners")
    print(f"Output: {output_file}")

    return df
