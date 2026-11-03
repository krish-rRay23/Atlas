# ATLAS — Production Backup, Disaster Recovery & Business Continuity Specification

**Product:** ATLAS — Asia Research Evidence Intelligence & Decision Workbench  
**Version:** 2.0.0  
**Compliance Standard:** ISO/IEC 27001 Business Continuity & NIST SP 800-34 Contingency Planning

---

## 1. Recovery Objectives

| Metric | Target | Rationale |
| :--- | :--- | :--- |
| **Recovery Point Objective (RPO)** | **< 1 Hour** | Ingestion feeds and human audit revisions must not lose more than 1 hour of research work in the event of hardware or storage node failure. |
| **Recovery Time Objective (RTO)** | **< 5 Minutes** | Complete database, parquet, and analytical cache restoration must complete in under 5 minutes from cold backup. |

---

## 2. Backup Architecture & Strategy

ATLAS employs a hybrid storage architecture:
1. **Relational Transactional Layer (`data/atlas.db`)**: SQLite with Write-Ahead Logging (WAL) mode.
2. **Analytical Columnar Layer (`data/atlas.duckdb`)**: DuckDB analytical tables.
3. **Columnar Parquet Store (`data/processed/*.parquet`)**: Immutable partition-ready evidence caches.

### Online Hot Backup Mechanics

- Standard filesystem copying (`cp` or `shutil.copy2`) of active SQLite databases in WAL mode risks copying mid-transaction pages, resulting in file corruption.
- ATLAS uses the official **SQLite Online Backup API** (`src_conn.backup(dest_conn)`), which safely serializes pages with shared read-locks without blocking concurrent readers or writers.
- DuckDB and Parquet stores are snapshot-synchronized with cryptographic SHA-256 integrity verification.
- Every backup generates a machine-readable `backup_manifest.json` detailing:
  - Timestamp (UTC)
  - Table observation, evidence, and memo record counts
  - Cryptographic SHA-256 hashes for all backup artifacts
  - Byte sizes

---

## 3. Disaster Recovery (DR) Execution Runbook

### Step 1: Execute Hot Online Backup
Run the backup CLI command:
```bash
python scripts/backup_and_restore.py --action backup
```
Output:
```text
[*] Starting ATLAS hot backup to: backups/atlas_backup_20261103_110847
[+] Backup completed successfully! Manifest written to backups/atlas_backup_20261103_110847/backup_manifest.json
    Observations: 646 | Evidence: 466 | Memos: 21
```

### Step 2: Disaster Recovery Verification & Restore
To restore data into a target deployment directory:
```bash
python scripts/backup_and_restore.py --action restore --manifest backups/atlas_backup_20261103_110847/backup_manifest.json --target data
```
Restoration Workflow:
1. **Cryptographic Checksum Verification**: Re-computes SHA-256 hashes of all artifacts; aborts immediately on any bit-flip or hash disparity.
2. **Atomic File Placement**: Copies validated files into the production directory.
3. **Database Integrity Audit**: Executes `PRAGMA integrity_check` on the restored SQLite database.
4. **Record Count Parity Audit**: Confirms exact match between recorded observations in manifest and restored table rows.

### Step 3: Automated DR Drill Execution
ATLAS provides an automated single-command test cycle that performs backup, SHA-256 validation, and restore verification in an isolated sandbox:
```bash
python scripts/backup_and_restore.py --action test-cycle
```
Status: Verified and Passing (zero parity errors, 100% SHA-256 match).
