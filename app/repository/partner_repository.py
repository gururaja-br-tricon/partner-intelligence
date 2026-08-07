import os

import pandas as pd


class PartnerRepository:

    def __init__(self, data_dir):
        self.data_dir = data_dir

        self.partners = self._load_csv("partner_master.csv")

        self.capabilities = self._load_csv("partner_capabilities.csv")

        self.programs = self._load_csv("partner_programs.csv")

        self.classifications = self._load_csv("partner_classifications.csv")

    def _load_csv(self, filename):
        file_path = os.path.join(self.data_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        return pd.read_csv(file_path)

    def get_partner(self, partner_id):
        result = self.partners[self.partners["partner_id"] == partner_id]

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    def get_partner_by_name(self, partner_name):
        result = self.partners[
            self.partners["partner_name"].str.lower() == partner_name.lower()
        ]

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    def get_capabilities(self, partner_id):
        result = self.capabilities[self.capabilities["partner_id"] == partner_id]

        return result.to_dict(orient="records")

    def get_programs(self, partner_id):
        result = self.programs[self.programs["partner_id"] == partner_id]

        return result.to_dict(orient="records")

    def get_classifications(self, partner_id):
        result = self.classifications[self.classifications["partner_id"] == partner_id]

        return result.to_dict(orient="records")

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
        result = self.partners.copy()

        if headquarters_state:
            result = result[result["headquarters_state"].str.lower() == headquarters_state.lower()]

        if headquarters_country:
            result = result[result["headquarters_country"].str.lower() == headquarters_country.lower()]

        if industry:
            result = result[result["industry"].str.lower() == industry.lower()]

        if status:
            result = result[result["status"].str.lower() == status.lower()]

        if capability:
            matching_partners = self.capabilities[self.capabilities["capability"].str.lower() == capability.lower()]

            if proficiency_level:
                matching_partners = matching_partners[matching_partners["proficiency_level"].str.lower()== proficiency_level.lower()]

            partner_ids = set(matching_partners["partner_id"])

            result = result[result["partner_id"].isin(partner_ids)]

        elif proficiency_level:
            matching_partners = self.capabilities[self.capabilities["proficiency_level"].str.lower() == proficiency_level.lower()]

            partner_ids = set(matching_partners["partner_id"])

            result = result[result["partner_id"].isin(partner_ids)]

        if vendor or program_name or partner_tier:
            matching_programs = self.programs.copy()

            if vendor:
                matching_programs = matching_programs[
                    matching_programs["vendor"].str.lower() == vendor.lower()
                ]

            if program_name:
                matching_programs = matching_programs[
                    matching_programs["program_name"].str.lower()
                    == program_name.lower()
                ]

            if partner_tier:
                matching_programs = matching_programs[
                    matching_programs["partner_tier"].str.lower()
                    == partner_tier.lower()
                ]

            partner_ids = set(matching_programs["partner_id"])

            result = result[result["partner_id"].isin(partner_ids)]

        if classification:
            matching_classifications = self.classifications[
                self.classifications["classification"].str.lower()
                == classification.lower()
            ]

            partner_ids = set(matching_classifications["partner_id"])

            result = result[result["partner_id"].isin(partner_ids)]

        return result.to_dict(orient="records")

    def search_by_capability(self, capability=None, proficiency_level=None):
        result = self.capabilities.copy()

        if capability:
            result = result[result["capability"].str.lower() == capability.lower()]

        if proficiency_level:
            result = result[
                result["proficiency_level"].str.lower() == proficiency_level.lower()
            ]

        return result.to_dict(orient="records")

    def search_by_program(
        self, vendor=None, program_name=None, partner_tier=None, status=None
    ):
        result = self.programs.copy()

        if vendor:
            result = result[result["vendor"].str.lower() == vendor.lower()]

        if program_name:
            result = result[result["program_name"].str.lower() == program_name.lower()]

        if partner_tier:
            result = result[result["partner_tier"].str.lower() == partner_tier.lower()]

        if status:
            result = result[result["status"].str.lower() == status.lower()]

        return result.to_dict(orient="records")

    def search_by_classification(self, classification=None, primary_only=False):
        result = self.classifications.copy()

        if classification:
            result = result[
                result["classification"].str.lower() == classification.lower()
            ]

        if primary_only:
            result = result[result["primary_classification"] == True]

        return result.to_dict(orient="records")

    def get_partner_profile(self, partner_id):
        partner = self.get_partner(partner_id)

        if not partner:
            return None

        return {
            "partner": partner,
            "capabilities": self.get_capabilities(partner_id),
            "programs": self.get_programs(partner_id),
            "classifications": self.get_classifications(partner_id),
        }
