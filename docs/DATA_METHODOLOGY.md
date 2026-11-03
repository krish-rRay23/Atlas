# Data Methodology & Transformation Protocols

## 1. Principles of Empirical Integrity

ATLAS enforces strict data integrity rules across all ingestion and analytical modules:

1. **Zero Data Fabrication**: Missing values in authoritative databases remain explicitly tagged as `missing` (`None`). Under no circumstances are missing values backfilled with zero, interpolated without notice, or hallucinated.
2. **Immutability of Raw Downloads**: All downloaded API responses and parsed source payloads are stored as immutable byte streams in `data/raw/`. Transformations produce normalized datasets in `data/processed/` without altering raw history.
3. **Cryptographic Provenance**: Every downloaded file has an associated SHA-256 hash computed at arrival and stored in `data/metadata/sources_manifest.json`.

---

## 2. Ingestion & Normalization Protocol

### 2.1 Geographic Identifiers
All economies are standardized to ISO 3166-1 alpha-3 codes:
- India: `IND`
- Indonesia: `IDN`
- Vietnam: `VNM`
- Thailand: `THA`
- Philippines: `PHL`

### 2.2 Numerical Standards
- Percentages: Stored as floating point numbers representing 0.0 to 100.0 (e.g., 89.02% is recorded as `89.02`).
- Large Numbers: Payment volumes are harmonized to billions of transactions (`billion_transactions`).
- Access Density: Bank branches and ATMs are normalized per 100,000 adult population (`per_100k_adults`), adopting the IMF FAS standard denominator.

---

## 3. Audited Data Divergence: Philippines Internet Penetration Figures

During data verification, an apparent divergence was detected in Philippines Internet Penetration (`IT.NET.USER.ZS`):
- **2023**: `77.87%`
- **2024**: `67.26%` (an apparent 10.61 percentage point decline).

### Forensic Lineage Investigation:
1. **Source Provenance**: Both figures are published directly within the World Bank WDI database (`data/raw/wb_IT_NET_USER_ZS.json`), with the underlying primary source recorded as the International Telecommunication Union (ITU).
2. **Methodological Context & Denominator Distinctions**:
   - **ITU Model Estimates vs Forecasting**: ITU produces country estimates using an econometric/machine-learning model when direct, standardized survey data are not yet officially processed for that reference year. The model incorporates historical surveys, mobile-broadband subscriptions, GDP per capita, and urbanization as predictor inputs, applying a country-level forecasting curve. This modeled projection yielded the 77.87% estimate for 2023.
   - **Denominator Differences**: World Bank WDI reports `IT.NET.USER.ZS` defined as *Internet users as a percentage of the **total population***.
   - **PSA NICTHS 2024 Survey**: In 2024, the Philippine Department of Information and Communications Technology (DICT) and Philippine Statistics Authority (PSA) released the *National ICT Household Survey (NICTHS 2024)*, which recorded individuals who used the internet in the past 3 months. Crucially, the PSA NICTHS survey denominator is restricted to the **household population aged 10 years and older** (excluding children under 10 and institutional populations), whereas WDI is benchmarked against the total population.
   - **Absence of Confirmed Revision Bulletin**: ITU has not issued an official revision bulletin explicitly stating whether or how the NICTHS 2024 microdata was ingested into the 2024 WDI series or if the decline reflects model recalibration against recent survey benchmarks. ATLAS explicitly does **not** imply that the two methodologies are identical or that a definitive methodological break has been confirmed by ITU.
3. **Treatment in ATLAS**:
   - The original observation values remain uncorrupted and unaltered.
   - The evidence ledger explicitly flags `EV-PHL_IT.NET.USER.ZS_2024` with `validation_status = 'caveat'`.
   - Reviewer notes specify: *"Methodological and denominator divergence: ITU 2023 estimate (77.87%) was derived from an econometric forecasting model using subscription and macroeconomic inputs against total population. The 2024 figure (67.26%) coincided with Philippine PSA NICTHS 2024 survey findings (which uses an age 10+ household population denominator). WDI measures % of total population. Flagged for review; no official ITU structural break bulletin confirmed."*

---

## 4. AsiaMetric 5-Dimensional Comparability Rules

When assessing two observations across economies, ATLAS evaluates five formal dimensions:

$$\text{Comparability Score} = \sum_{d=1}^{5} w_d \cdot C_d$$

Where $C_d \in \{0, 1\}$ represents consistency in:
1. **Unit Consistency ($C_1$)**: E.g., comparing percentage to percentage.
2. **Denominator Consistency ($C_2$)**: E.g., adults aged 15+ vs total population vs total cellular SIMs.
3. **Target Population Consistency ($C_3$)**: Household survey respondent vs commercial financial institution infrastructure.
4. **Methodology Consistency ($C_4$)**: Random sample survey vs statutory payment switch logs.
5. **Reference Period Consistency ($C_5$)**: Temporal alignment within $\le 2$ years.

### Rule Hierarchy
- **RULE_CONSTRUCT_DIVERGENCE**: If indicator constructs measure fundamentally different phenomena, classification is `not_comparable`. Cross-country rankings are blocked.
- **RULE_PAYMENT_RAILS_CAVEAT**: Fast payment volumes (UPI, QRIS, PromptPay) are classified as `comparable_with_caveats` due to population disparities and P2P vs P2M structural differences.
- **RULE_FULL_HARMONIZATION**: If all 5 dimensions match, classification is `comparable`.
- **RULE_TEMPORAL_CAVEAT**: If dimensions match but reference periods diverge by $\le 2$ years, classification is `comparable_with_caveats`.
