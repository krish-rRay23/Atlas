"""ATLAS Source Registry.

Maintains metadata, provenance, methodology, and authoritative URLs
for all macroeconomic, inclusion, payment, and benchmark sources.
"""

from typing import Dict, List
from atlas.core.models import SourceMetadata, IndicatorDefinition

OFFICIAL_SOURCES: Dict[str, SourceMetadata] = {
    "WB_FINDEX": SourceMetadata(
        source_id="WB_FINDEX",
        name="World Bank Global Findex Database",
        publisher="World Bank Group",
        url="https://www.worldbank.org/en/publication/globalfindex",
        source_type="international_organization",
        methodology="Nationally representative survey of approximately 1,000 randomly selected adults (ages 15+) per economy. Triennial waves with country-level sampling weights.",
        coverage_geos=["IND", "IDN", "VNM", "THA", "PHL"],
        reference_period="2011-2024",
        publication_date="2024-10-01",
        retrieval_date="2026-11-03",
        data_format="json_api",
        quality_score=0.98,
        limitations="Survey-based; subject to self-reporting bias and sampling error. Collected periodically (triennial) rather than continuously."
    ),
    "IMF_FAS": SourceMetadata(
        source_id="IMF_FAS",
        name="IMF Financial Access Survey (FAS) [via World Bank API Mirror]",
        publisher="International Monetary Fund / World Bank",
        url="https://data.imf.org/?sk=E5DCCDCD-79C1-466A-BD55-E49755B44C69",
        source_type="international_organization",
        methodology="Annual administrative supply-side data collected directly from central banks and financial regulatory authorities across 189 jurisdictions, mirrored via World Bank Data API.",
        coverage_geos=["IND", "IDN", "VNM", "THA", "PHL"],
        reference_period="2015-2024",
        publication_date="2024-10-15",
        retrieval_date="2026-11-03",
        data_format="json_api",
        quality_score=0.97,
        limitations="Supply-side data; counts access points (branches, ATMs) and registered accounts rather than distinct individuals. Excludes informal channels."
    ),
    "WB_WDI": SourceMetadata(
        source_id="WB_WDI",
        name="World Development Indicators & ITU Telecommunications",
        publisher="World Bank & International Telecommunication Union (ITU)",
        url="https://datatopics.worldbank.org/world-development-indicators/",
        source_type="international_organization",
        methodology="Harmonized cross-country macroeconomic, demographic, and ICT infrastructure time-series compiled from national statistical offices and international agencies.",
        coverage_geos=["IND", "IDN", "VNM", "THA", "PHL"],
        reference_period="2015-2024",
        publication_date="2024-10-08",
        retrieval_date="2026-11-03",
        data_format="json_api",
        quality_score=0.99,
        limitations="Cross-country differences in definitions of internet user and active cellular subscriptions."
    ),
    "GSMA_ME": SourceMetadata(
        source_id="GSMA_ME",
        name="GSMA Mobile Economy Asia Pacific Report",
        publisher="GSM Association (GSMA Intelligence)",
        url="https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-economy/asiapacific/",
        source_type="industry_association",
        methodology="Proprietary econometric modeling based on primary operator reporting, consumer surveys, and regulatory disclosures across APAC telecom markets.",
        coverage_geos=["IND", "IDN", "VNM", "THA", "PHL"],
        reference_period="2023-2024",
        publication_date="2024-07-20",
        retrieval_date="2026-11-03",
        data_format="report_pdf_extract",
        quality_score=0.92,
        limitations="Market estimates and operator-reported connection shares; smartphone adoption reflects SIM connections rather than unique individuals."
    ),
    "RBI_NPCI": SourceMetadata(
        source_id="RBI_NPCI",
        name="Reserve Bank of India & NPCI Payment System Statistics",
        publisher="Reserve Bank of India / National Payments Corporation of India",
        url="https://www.rbi.org.in/Scripts/BS_ViewBulletin.aspx",
        source_type="central_bank",
        methodology="Official statutory payment system settlement and clearing logs for UPI, NEFT, RTGS, and IMPS.",
        coverage_geos=["IND"],
        reference_period="2020-2024",
        publication_date="2024-11-01",
        retrieval_date="2026-11-03",
        data_format="bulletin_extract",
        quality_score=0.99,
        limitations="Transaction counts include person-to-person (P2P) transfers as well as merchant payments (P2M)."
    ),
    "BI_STAT": SourceMetadata(
        source_id="BI_STAT",
        name="Bank Indonesia Payment System & QRIS Official Statistics",
        publisher="Bank Indonesia (Central Bank)",
        url="https://www.bi.go.id/en/statistik/ekonomi-keuangan/ssp/default.aspx",
        source_type="central_bank",
        methodology="Central bank supervisory data covering national retail payment switches, QRIS transactions, BI-FAST, and electronic money (e-money).",
        coverage_geos=["IDN"],
        reference_period="2020-2024",
        publication_date="2024-12-31",
        retrieval_date="2026-11-03",
        data_format="central_bank_disclosure",
        quality_score=0.99,
        limitations="Merchants include multi-QRIS registrations; user metrics represent registered app accounts."
    ),
    "BOT_PS": SourceMetadata(
        source_id="BOT_PS",
        name="Bank of Thailand Payment Systems Bulletin & PromptPay Reports",
        publisher="Bank of Thailand",
        url="https://www.bot.or.th/en/statistics/payment.html",
        source_type="central_bank",
        methodology="Supervisory oversight of the National ITMX retail payment infrastructure, PromptPay real-time fund transfer, and cross-border QR linkages.",
        coverage_geos=["THA"],
        reference_period="2020-2024",
        publication_date="2024-11-30",
        retrieval_date="2026-11-03",
        data_format="central_bank_disclosure",
        quality_score=0.99,
        limitations="PromptPay registration IDs exceed total population because individuals may link Citizen ID and mobile numbers."
    ),
    "BSP_FIRD": SourceMetadata(
        source_id="BSP_FIRD",
        name="Bangko Sentral ng Pilipinas Financial Inclusion Dashboard & E-Payments Report",
        publisher="Bangko Sentral ng Pilipinas",
        url="https://www.bsp.gov.ph/Pages/InclusiveFinance/FinancialInclusionReports.aspx",
        source_type="central_bank",
        methodology="Annual survey of digital retail payments under the Digital Payments Transformation Roadmap, integrating PESONet, InstaPay, and merchant POS transactions.",
        coverage_geos=["PHL"],
        reference_period="2020-2024",
        publication_date="2024-10-31",
        retrieval_date="2026-11-03",
        data_format="central_bank_disclosure",
        quality_score=0.99,
        limitations="Retail payment volume/value share methodology applies to merchant payments, government disbursements, and person-to-person."
    ),
    "SBV_STAT": SourceMetadata(
        source_id="SBV_STAT",
        name="State Bank of Vietnam Payment Department Official Disclosures",
        publisher="State Bank of Vietnam / NAPAS",
        url="https://sbv.gov.vn/",
        source_type="central_bank",
        methodology="National payment supervisory logs, NAPAS interbank switching reports, and licensed payment intermediary returns.",
        coverage_geos=["VNM"],
        reference_period="2020-2024",
        publication_date="2024-12-31",
        retrieval_date="2026-11-03",
        data_format="central_bank_disclosure",
        quality_score=0.97,
        limitations="Rapid regulatory shifts; Mobile Money pilot reporting is distinct from commercial bank accounts."
    )
}

OFFICIAL_INDICATORS: List[IndicatorDefinition] = [
    # Global Findex
    IndicatorDefinition(
        indicator_code="FX.OWN.TOTL.ZS",
        name="Account Ownership (% of population ages 15+)",
        category="financial_inclusion",
        unit="percentage",
        denominator="Total population aged 15+",
        target_population="Adults aged 15+",
        source_id="WB_FINDEX",
        description="Percentage of respondents who report having an account at a bank or other type of financial institution, or personally using a mobile money service in the past 12 months."
    ),
    IndicatorDefinition(
        indicator_code="FX.OWN.TOTL.FE.ZS",
        name="Account Ownership, Female (% of females ages 15+)",
        category="financial_inclusion",
        unit="percentage",
        denominator="Female population aged 15+",
        target_population="Female adults aged 15+",
        source_id="WB_FINDEX",
        description="Percentage of female respondents reporting account ownership."
    ),
    IndicatorDefinition(
        indicator_code="FX.OWN.TOTL.MA.ZS",
        name="Account Ownership, Male (% of males ages 15+)",
        category="financial_inclusion",
        unit="percentage",
        denominator="Male population aged 15+",
        target_population="Male adults aged 15+",
        source_id="WB_FINDEX",
        description="Percentage of male respondents reporting account ownership."
    ),
    IndicatorDefinition(
        indicator_code="FX.OWN.TOTL.RU.ZS",
        name="Account Ownership, Rural (% of rural population ages 15+)",
        category="financial_inclusion",
        unit="percentage",
        denominator="Rural population aged 15+",
        target_population="Rural adults aged 15+",
        source_id="WB_FINDEX",
        description="Percentage of rural respondents reporting account ownership."
    ),
    IndicatorDefinition(
        indicator_code="FX.OWN.TOTL.PL.ZS",
        name="Account Ownership, Poorest 40% (% of poorest 40% ages 15+)",
        category="financial_inclusion",
        unit="percentage",
        denominator="Poorest 40% population aged 15+",
        target_population="Poorest 40% income quintile",
        source_id="WB_FINDEX",
        description="Percentage of adults in the poorest 40% of households who report account ownership."
    ),

    # IMF Financial Access Survey
    IndicatorDefinition(
        indicator_code="FB.CBK.BRCH.P5",
        name="Commercial Bank Branches (per 100,000 adults)",
        category="infrastructure",
        unit="count_per_100k_adults",
        denominator="Adult population (100,000)",
        target_population="Commercial bank physical retail presence",
        source_id="IMF_FAS",
        description="Number of commercial bank retail branch offices per 100,000 adults, sourced from IMF Financial Access Survey."
    ),
    IndicatorDefinition(
        indicator_code="FB.ATM.TOTL.P5",
        name="Automated Teller Machines (ATMs) (per 100,000 adults)",
        category="infrastructure",
        unit="count_per_100k_adults",
        denominator="Adult population (100,000)",
        target_population="Physical ATM infrastructure",
        source_id="IMF_FAS",
        description="Number of automated teller machines per 100,000 adults, sourced from IMF Financial Access Survey."
    ),

    # ITU & World Bank WDI
    IndicatorDefinition(
        indicator_code="IT.NET.USER.ZS",
        name="Individuals Using the Internet (% of population)",
        category="macro_demographic",
        unit="percentage",
        denominator="Total resident population",
        target_population="All residents",
        source_id="WB_WDI",
        description="Percentage of population who have used the internet from any location in the last 3 months via computer, mobile phone, digital TV, or game console."
    ),
    IndicatorDefinition(
        indicator_code="IT.CEL.SETS.P2",
        name="Mobile Cellular Subscriptions (per 100 people)",
        category="macro_demographic",
        unit="subscriptions_per_100",
        denominator="100 residents",
        target_population="Active SIM connections",
        source_id="WB_WDI",
        description="Subscriptions to a public mobile telephone service using cellular technology, including postpaid and active prepaid subscriptions."
    ),
    IndicatorDefinition(
        indicator_code="NY.GDP.PCAP.CD",
        name="GDP Per Capita (current US$)",
        category="macro_demographic",
        unit="usd",
        denominator="Midyear total population",
        target_population="National economy",
        source_id="WB_WDI",
        description="Gross domestic product divided by midyear population, in current U.S. dollars."
    ),

    # GSMA Mobile Economy
    IndicatorDefinition(
        indicator_code="GSMA.SMARTPHONE.PCT",
        name="Smartphone Adoption (% of total mobile connections)",
        category="macro_demographic",
        unit="percentage",
        denominator="Total cellular connections (excluding cellular IoT)",
        target_population="Mobile subscriber connections",
        source_id="GSMA_ME",
        description="Percentage of mobile connections that are smartphone devices, from GSMA Intelligence."
    ),

    # National Payment Schemes
    IndicatorDefinition(
        indicator_code="NAT.DIGITAL.PAY.VOL",
        name="National Fast/Digital Payment Annual Volume (Billion transactions)",
        category="digital_payments",
        unit="billion_transactions",
        denominator="National retail payment ecosystem",
        target_population="Domestic transactions",
        source_id="RBI_NPCI",
        description="Annual transaction volume processed by the primary national instant retail payment rails (India UPI, Indonesia QRIS, Thailand PromptPay, Philippines InstaPay/PESONet, Vietnam NAPAS/VietQR)."
    ),
    IndicatorDefinition(
        indicator_code="NAT.DIGITAL.PAY.SHARE",
        name="Share of Digital Payments in Total Retail Transactions (Volume %)",
        category="digital_payments",
        unit="percentage",
        denominator="Total monthly/annual retail transactions (cash + digital)",
        target_population="Retail payment transactions",
        source_id="BSP_FIRD",
        description="Percentage share of monthly retail transactions conducted via electronic/digital channels as reported by the central monetary authority."
    )
]

# Source-specific freshness policies & licensing governance
DATASET_FRESHNESS_POLICIES: Dict[str, Dict[str, Any]] = {
    "WB_FINDEX": {
        "cadence": "triennial",
        "max_age_months": 36,
        "license": "Creative Commons Attribution 4.0 International (CC-BY 4.0)",
        "next_expected_release": "2027-Q4",
        "methodology_type": "national_stratified_survey"
    },
    "IMF_FAS": {
        "cadence": "annual",
        "max_age_months": 15,
        "license": "IMF Open Data Terms of Use (Attribution Required)",
        "next_expected_release": "2025-Q4",
        "methodology_type": "statutory_administrative_census"
    },
    "WB_WDI": {
        "cadence": "annual",
        "max_age_months": 12,
        "license": "CC-BY 4.0 (World Bank Open Data)",
        "next_expected_release": "2025-Q3",
        "methodology_type": "harmonized_international_series"
    },
    "GSMA_ME": {
        "cadence": "annual",
        "max_age_months": 14,
        "license": "GSMA Intelligence Proprietary / Academic Research Use",
        "next_expected_release": "2025-Q3",
        "methodology_type": "econometric_operator_triangulation"
    },
    "RBI_NPCI": {
        "cadence": "monthly",
        "max_age_months": 3,
        "license": "Government of India National Open Data License / RBI Public Domain",
        "next_expected_release": "2026-12",
        "methodology_type": "payment_switch_settlement_log"
    },
    "BI_STAT": {
        "cadence": "monthly",
        "max_age_months": 3,
        "license": "Bank Indonesia Public Disclosures",
        "next_expected_release": "2026-12",
        "methodology_type": "payment_switch_settlement_log"
    },
    "BOT_STAT": {
        "cadence": "quarterly",
        "max_age_months": 4,
        "license": "Bank of Thailand Public Disclosures",
        "next_expected_release": "2026-12",
        "methodology_type": "payment_switch_settlement_log"
    },
    "BSP_FIRD": {
        "cadence": "semi_annual",
        "max_age_months": 8,
        "license": "Bangko Sentral ng Pilipinas Public Disclosures",
        "next_expected_release": "2027-Q1",
        "methodology_type": "monetary_authority_survey_and_switch_audit"
    },
    "SBV_PAY": {
        "cadence": "annual",
        "max_age_months": 14,
        "license": "State Bank of Vietnam Official Disclosures",
        "next_expected_release": "2027-Q1",
        "methodology_type": "central_bank_banking_bulletin"
    }
}

def evaluate_source_freshness(source_id: str, last_retrieval_date_str: str) -> Dict[str, Any]:
    """Evaluate whether an ingested source satisfies its source-specific freshness policy."""
    policy = DATASET_FRESHNESS_POLICIES.get(source_id, {
        "cadence": "annual",
        "max_age_months": 12,
        "license": "Public Domain / Standard Fair Use",
        "next_expected_release": "TBD"
    })
    
    import datetime
    try:
        retrieval_dt = datetime.datetime.strptime(last_retrieval_date_str[:10], "%Y-%m-%d")
        now = datetime.datetime.now()
        age_days = (now - retrieval_dt).days
        age_months = age_days / 30.4375
        
        is_fresh = age_months <= policy["max_age_months"]
        status = "fresh" if is_fresh else ("acceptable" if age_months <= policy["max_age_months"] * 1.5 else "stale")
        
        return {
            "source_id": source_id,
            "status": status,
            "age_months": round(age_months, 1),
            "max_age_months": policy["max_age_months"],
            "cadence": policy["cadence"],
            "license": policy["license"],
            "next_expected_release": policy["next_expected_release"]
        }
    except Exception:
        return {
            "source_id": source_id,
            "status": "unknown",
            "age_months": 0.0,
            "cadence": policy.get("cadence", "annual"),
            "license": policy.get("license", "Unknown")
        }

