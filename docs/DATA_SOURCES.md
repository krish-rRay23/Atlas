# Authoritative Data Sources Catalogue

ATLAS strictly prohibits data fabrication or synthetic market inflation. All reported market metrics originate from authoritative international organizations, central banks, and industry statistical bodies.

| Source ID | Name | Publisher | Coverage | Reference Period | Official Lineage & URL | Collection Method | Quality Score |
|---|---|---|---|---|---|---|---|
| `WB_FINDEX` | World Bank Global Findex Database | World Bank Group | IND, IDN, VNM, THA, PHL | 2011–2024 | [worldbank.org/globalfindex](https://www.worldbank.org/en/publication/globalfindex) | Triennial nationally representative survey of ~1,000 adults (15+) per economy. | 0.98 |
| `IMF_FAS` | Financial Access Survey (FAS) | International Monetary Fund (via World Bank API Mirror) | IND, IDN, VNM, THA, PHL | 2015–2024 | [data.imf.org](https://data.imf.org/?sk=E5DCCDCD-79C1-466A-BD55-E49755B44C69) / [api.worldbank.org](https://api.worldbank.org/v2/) | Annual administrative supply-side reporting from central banks, ingested via World Bank Data API mirror. | 0.97 |
| `WB_WDI` | World Development Indicators & ITU | World Bank / ITU | IND, IDN, VNM, THA, PHL | 2011–2024 | [datatopics.worldbank.org](https://datatopics.worldbank.org/world-development-indicators/) | Harmonized cross-country macroeconomic, demographic, and ICT infrastructure time-series. | 0.99 |
| `GSMA_ME` | Mobile Economy Asia Pacific Report | GSMA Intelligence | IND, IDN, VNM, THA, PHL | 2023–2024 | [gsma.com](https://www.gsma.com/solutions-and-impact/connectivity-for-good/mobile-economy/asiapacific/) | Econometric modeling and primary operator reporting across APAC telecommunications. | 0.92 |
| `RBI_NPCI` | Payment System Indicators & UPI Statistics | Reserve Bank of India / NPCI | IND | 2020–2024 | [rbi.org.in](https://www.rbi.org.in/) | Statutory payment system clearing and settlement transaction logs. | 0.99 |
| `BI_STAT` | QRIS & Payment System Disclosures | Bank Indonesia | IDN | 2020–2024 | [bi.go.id](https://www.bi.go.id/) | Supervisory oversight data covering national retail payment switches and QRIS registries. | 0.99 |
| `BOT_PS` | PromptPay & Payment Systems Bulletin | Bank of Thailand | THA | 2020–2024 | [bot.or.th](https://www.bot.or.th/) | Oversight of the National ITMX retail payment infrastructure and PromptPay switches. | 0.99 |
| `BSP_FIRD` | Report on the Status of Digital Payments | Bangko Sentral ng Pilipinas | PHL | 2020–2024 | [bsp.gov.ph](https://www.bsp.gov.ph/) | Annual retail payment transformation survey integrating PESONet, InstaPay, and POS data. | 0.99 |
| `SBV_STAT` | Non-Cash Payment Review & Digital Transformation | State Bank of Vietnam / NAPAS | VNM | 2020–2024 | [sbv.gov.vn](https://sbv.gov.vn/) | National payment department supervisory logs and NAPAS interbank switching statistics. | 0.97 |

---

## 2. Ingestion Classification & Data Lineage Disclosure

1. **Automated API Downloads (`data/raw/wb_*.json`)**:
   - Ingested directly from `https://api.worldbank.org/v2/`.
   - Immutable raw API responses stored as received with SHA-256 validation.
2. **Curated Primary Administrative Observations (`data/raw/central_banks_and_gsma.json`)**:
   - This file contains **curated and normalized primary observations** extracted from statutory central bank publications and GSMA reports.
   - It is **not** raw PDF binary bytes; rather, each entry carries exact page, table, and bulletin citations for full auditability.
3. **IMF FAS Mirroring**:
   - Access density indicators (`FB.CBK.BRCH.P5` and `FB.ATM.TOTL.P5`) were retrieved via the **World Bank Data API mirror** of the IMF Financial Access Survey, rather than the IMF SDMX endpoint directly.

---

## 3. Benchmark Datasets

| Benchmark | Dataset Split | Evaluated / Available | Primary Task Evaluated | Source / Reference |
|---|---|---|---|---|
| **FinQA** | Official Test Split | 100 / 1,147 samples | Financial numerical reasoning & multi-step arithmetic | Chen et al., EMNLP 2021 |
| **TAT-QA** | Official Dev Split | 75 / 1,668 questions | Hybrid table and textual question answering | Zhu et al., ACL 2021 |
| **In-Domain Gold** | Hand-Verified Ground Truth | 35 / 35 test cases | Numeric extraction, comparability traps, and contradiction detection | ATLAS Research Team 2024 |
