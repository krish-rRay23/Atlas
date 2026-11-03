# ATLAS — Production Security Architecture & Governance Specification

**Product:** ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Classification:** Enterprise Security Architecture Specification  
**Version:** 2.0.0 (Production-Grade)  
**Standard Compliance:** OWASP Top 10 for LLM Applications (2025), NIST AI Risk Management Framework (AI RMF 1.0)

---

## 1. Executive Summary

This document specifies the defensive controls, authentication protocols, authorization models, and input/output sanitization pipelines implemented in ATLAS to ensure zero trust, deterministic integrity, and complete isolation of research intelligence operations.

---

## 2. Authentication & Role-Based Access Control (RBAC)

ATLAS implements a dual-mode authentication scheme supporting enterprise API keys and cryptographic bearer tokens via `atlas.core.security`.

### Role Hierarchy & Matrix

| Role | Permissions | Use Case |
| :--- | :--- | :--- |
| **Admin** | `all`, `manage_users`, `ingest`, `generate`, `review`, `read` | Platform administrators, operational DevOps |
| **Researcher** | `create_project`, `ingest`, `generate`, `read` | Financial analysts, quantitative researchers |
| **Reviewer** | `review_evidence`, `approve_claims`, `read` | Compliance officers, senior audit researchers |
| **Reader** | `read` | Stakeholders, executives, read-only viewers |

### Enforcement Mechanics

- **Authentication Dependency (`get_current_user`)**: Validates the `X-ATLAS-API-KEY` HTTP header or `Authorization: Bearer <token>`.
- **Authorization Dependency (`require_role([...])`)**: Enforces endpoint-level RBAC prior to business logic execution. Unauthenticated requests receive HTTP 401 Unauthorized; insufficient permissions yield HTTP 403 Forbidden.
- **Credential Storage**: Cryptographically hashed using SHA-256 with 16-byte cryptographically secure pseudorandom salt (`secrets.token_hex(16)`).

---

## 3. OWASP Top 10 for LLM Applications — Control Mapping

| OWASP Vulnerability | Risk Scenario in ATLAS | Implemented Defense Mechanism | Source File |
| :--- | :--- | :--- | :--- |
| **LLM01: Prompt Injection** | Adversarial text in research questions or scraped documents attempting to override system prompts or bypass evidence requirements. | `sanitize_prompt()` strips delimiter escapes (`<\|im_start\|>`, `<\|im_end\|>`), command overrides (`ignore previous instructions`, `system override`), and script tags. Enforces 16,000 character maximum input bounds. | `atlas/synthesis/llm_client.py` |
| **LLM02: Insecure Output Handling** | LLM-generated code or unescaped HTML injected into frontend visualization dashboards. | All LLM outputs are parsed into strictly typed Pydantic models (`ResearchMemo`, `ResearchMemoSection`). Markdown is rendered safely through Streamlit without `unsafe_allow_html=True` for dynamic LLM content. | `atlas/synthesis/engine.py` |
| **LLM03: Training Data Poisoning** | Ingestion of corrupted or falsified statistical figures from malicious mirrors. | Cryptographic SHA-256 hash checking against official releases (`registry.py`). Strict TLS certificate verification and source quality score gating. | `atlas/sources/fetcher.py` |
| **LLM04: Model Denial of Service** | Unbounded input queries consuming excessive tokens and locking compute threads. | Input token bounding, thread pool execution (`_job_executor`), configurable request timeouts, and client rate limiting. | `atlas/core/jobs.py` |
| **LLM05: Supply Chain Vulnerabilities** | Compromised third-party packages or untrusted dependencies. | Dependency pinning in `pyproject.toml`, vulnerability scanning via automated CI workflows, and zero unvetted runtime dependencies. | `pyproject.toml`, `.github/workflows/ci.yml` |
| **LLM06: Sensitive Information Disclosure** | Accidental leakage of API keys, server paths, or internal metadata in synthesis outputs or error messages. | Global exception handlers in `StructuredLoggingMiddleware` sanitize stack traces before returning generic error payloads. Environment variables are loaded through Pydantic BaseSettings with hidden secrets. | `atlas/core/config.py`, `atlas/core/observability.py` |
| **LLM07: Insecure Plugin Design** | External connectors executing arbitrary SQL or network calls without validation. | Data connectors are read-only REST fetchers with bounded parameter schemas and circuit-breaker backoffs. | `atlas/sources/fetcher.py` |
| **LLM08: Excessive Agency** | Model autonomously altering evidence ledger records or publishing research deliverables without review. | Strict factual separation: LLMs can propose research memos, but validation is computed deterministically by `ClaimValidationEngine`, and final approval requires human audit revision. | `atlas/evidence/claim_validator.py`, `atlas/core/models.py` |
| **LLM09: Overreliance (Hallucination)** | LLM fabricating macroeconomic figures or inventing synthetic citations. | Deterministic citation validation: all `EV-...` citations in LLM responses are cross-referenced against the local evidence ledger; ungrounded citations are stripped. Numeric assertions are audited against tolerance bounds. | `atlas/synthesis/llm_client.py`, `atlas/evidence/claim_validator.py` |
| **LLM10: Model Theft** | Exfiltration of proprietary prompts or fine-tuned parameters. | Hardcoded prompt templates with strict parameter binding; no client-exposed raw system prompts. | `atlas/synthesis/engine.py` |

---

## 4. Network Security & SSRF Protection

### Server-Side Request Forgery (SSRF) Defense

To prevent internal network enumeration or cloud metadata service exfiltration, all external URLs requested by data ingestion connectors must pass `validate_url_safety()`:

- **Protocol Restriction**: Only `http` and `https` schemes permitted.
- **Loopback & Private Network Blocking**: Rejects `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, and `::1/128`.
- **Cloud Metadata Service Blocking**: Explicitly forbids `169.254.169.254` (AWS, GCP, Azure instance metadata) and `metadata.google.internal`.

### Path Traversal Defense

File exports and disk access use `safe_path_join()`, which strips path separators, replaces non-alphanumeric characters with safe underscores, resolves absolute canonical paths, and asserts prefix containment within designated sandboxes.

---

## 5. Security Verification Summary

Security controls are verified via automated pytest suites:
- SSRF protection: `tests/test_security.py::test_url_safety_ssrf_protection` (PASSED)
- Path traversal: `tests/test_security.py::test_safe_path_join_traversal_defense` (PASSED)
- Prompt injection: `tests/test_security.py::test_prompt_injection_sanitization` (PASSED)
- Password hashing & salt: `tests/test_security.py::test_password_hashing` (PASSED)
- RBAC permissions matrix: `tests/test_security.py::test_rbac_matrix` (PASSED)
