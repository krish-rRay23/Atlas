# Security, Governance & Responsible AI Controls

## 1. Governance Reference Framework

ATLAS adopts the **NIST AI Risk Management Framework (AI RMF 1.0)** and its **Generative AI Profile** as the operational benchmark for responsible AI deployment in high-stakes research workflows:

- **GOVERN**: Institutional accountability, evidence immutability, and explicit analyst approval gateways.
- **MAP**: Explicit geographic (5 target economies), temporal (2011–2024), and domain boundaries.
- **MEASURE**: Quantitative tracking of citation precision, numerical fidelity, and contradiction rates via RAGAS, ALCE, and FinQA.
- **MANAGE**: Deterministic rule engines that automatically block ungrounded claims and invalid cross-country rankings.

---

## 2. Security Architecture & Threat Mitigation

### 2.1 Prompt Injection & Untrusted Data Defense
- Public web documents, PDFs, and API payloads are treated strictly as **untrusted external data**.
- Retrieved texts are isolated into structured data fields before reaching the synthesis engine. No executable instructions embedded within external source documents are interpreted by the model.

### 2.2 Credential Protection
- API keys (`OPENAI_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `GEMINI_API_KEY`) are read strictly from environment variables.
- System logs (`model_logs` table) store token counts and costs, never echoing API keys, bearer tokens, or raw authorization headers.

### 2.3 Sandboxed Execution & Path Traversal Prevention
- File operations are restricted to `data/` and project subdirectories.
- Path parameters are validated against whitelist directories to prevent traversal attacks (`../`).

### 2.4 Human-in-the-Loop Oversight
- Factual claims are automatically marked with validation statuses (`supported`, `partially_supported`, `contradicted`, `unverified`).
- Analytical implications and strategic recommendations are explicitly quarantined in Section 11 of research memos as *interpretations*, requiring human analyst confirmation before client distribution.

