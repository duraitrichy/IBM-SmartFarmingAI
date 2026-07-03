"""
government_schemes.py — Government agricultural scheme data + RAG lookup.
"""

from typing import Any, Dict, List
from loguru import logger


SCHEMES_DB: List[Dict[str, Any]] = [
    {
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "category": "Income Support",
        "benefit": "₹6,000/year in 3 equal instalments directly to bank account",
        "eligibility": "Small and marginal farmers with up to 2 hectares of land",
        "application": "Register at pmkisan.gov.in or nearest CSC centre",
        "website": "https://pmkisan.gov.in",
        "state": "All India",
    },
    {
        "name": "PM Fasal Bima Yojana",
        "full_name": "Pradhan Mantri Fasal Bima Yojana",
        "category": "Crop Insurance",
        "benefit": "Crop loss compensation for natural calamities, pests, diseases",
        "eligibility": "All farmers growing notified crops in notified areas",
        "application": "Register through nearest bank branch or Common Service Centre",
        "website": "https://pmfby.gov.in",
        "state": "All India",
    },
    {
        "name": "PM Krishi Sinchai Yojana",
        "full_name": "Pradhan Mantri Krishi Sinchayee Yojana",
        "category": "Irrigation",
        "benefit": "55% subsidy on drip/sprinkler irrigation (SC/ST farmers get 75%)",
        "eligibility": "All farmers; preference to small and marginal",
        "application": "Apply through state agriculture department",
        "website": "https://pmksy.gov.in",
        "state": "All India",
    },
    {
        "name": "Soil Health Card Scheme",
        "full_name": "National Mission for Sustainable Agriculture — Soil Health Card",
        "category": "Soil Health",
        "benefit": "Free soil testing and personalised nutrient management card every 2 years",
        "eligibility": "All farmers",
        "application": "Contact nearest Krishi Vigyan Kendra or soil testing laboratory",
        "website": "https://soilhealth.dac.gov.in",
        "state": "All India",
    },
    {
        "name": "e-NAM",
        "full_name": "National Agriculture Market",
        "category": "Market Access",
        "benefit": "Sell crops online across India; better price discovery; reduced middlemen",
        "eligibility": "All registered farmers with Aadhaar and bank account",
        "application": "Register at enam.gov.in or nearest mandi",
        "website": "https://enam.gov.in",
        "state": "All India",
    },
    {
        "name": "KCC",
        "full_name": "Kisan Credit Card",
        "category": "Credit",
        "benefit": "Revolving credit up to ₹3 lakh at 4% interest (with timely repayment)",
        "eligibility": "Farmers, tenant farmers, sharecroppers, SHGs",
        "application": "Apply at nearest bank or co-operative society",
        "website": "https://www.nabard.org",
        "state": "All India",
    },
    {
        "name": "PM-AASHA",
        "full_name": "Pradhan Mantri Annadata Aay Sanrakshan Abhiyan",
        "category": "Price Support",
        "benefit": "MSP-based procurement; price deficiency payment up to 15%",
        "eligibility": "Registered farmers growing notified oilseeds, pulses, copra",
        "application": "Register through state NAFED portal",
        "website": "https://nafed-india.com",
        "state": "All India",
    },
    {
        "name": "PMEGP",
        "full_name": "Prime Minister's Employment Generation Programme",
        "category": "Agri-business",
        "benefit": "15–35% subsidy for agro-processing units up to ₹25 lakh project cost",
        "eligibility": "Individuals 18+ years; educational qualification: Class VIII for projects above ₹10 lakh",
        "application": "Apply through KVIC district office or online portal",
        "website": "https://www.kviconline.gov.in",
        "state": "All India",
    },
]


class GovernmentSchemesTool:
    """Provides scheme data via rule-based lookup and keyword search."""

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Return schemes relevant to the query."""
        query_lower = query.lower()
        matches = []
        for scheme in SCHEMES_DB:
            text = (
                scheme["name"] + scheme["full_name"] +
                scheme["category"] + scheme["benefit"] +
                scheme["eligibility"]
            ).lower()
            if any(kw in text for kw in query_lower.split()):
                matches.append(scheme)
        return matches or SCHEMES_DB[:3]

    def get_all(self) -> List[Dict[str, Any]]:
        return SCHEMES_DB

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        cat = category.lower()
        return [s for s in SCHEMES_DB if cat in s["category"].lower()]

    def format_for_display(self, schemes: List[Dict[str, Any]]) -> str:
        lines = []
        for s in schemes:
            lines.append(
                f"**{s['name']}** ({s['full_name']})\n"
                f"  Category: {s['category']}\n"
                f"  Benefit: {s['benefit']}\n"
                f"  Eligibility: {s['eligibility']}\n"
                f"  Apply: {s['application']}\n"
                f"  Website: {s['website']}\n"
            )
        return "\n".join(lines)
