"""ATLAS Production Backup, Checksum Verification, and Recovery Script.

Provides enterprise online hot backups for SQLite with Write-Ahead Logging (WAL),
DuckDB analytical data stores, Parquet caches, and cryptographic SHA-256 verification.
"""

import os
import sys
import json
import shutil
import sqlite3
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from atlas.core.config import SQLITE_DB_PATH, DUCKDB_PATH, PROCESSED_DATA_DIR
from atlas.core.db import get_sqlite_conn

def compute_sha256(filepath: Path) -> str:
    """Compute cryptographic SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_backup(backup_root: Path = Path("backups")) -> Path:
    """Perform hot consistent backup of SQLite relational DB and DuckDB / Parquet stores."""
    now_ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"atlas_backup_{now_ts}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting ATLAS hot backup to: {backup_dir}")

    # 1. Hot SQLite backup via SQLite Online Backup API (thread-safe, WAL-safe)
    dest_sqlite = backup_dir / "atlas.db"
    src_conn = get_sqlite_conn()
    dest_conn = sqlite3.connect(str(dest_sqlite))
    with dest_conn:
        src_conn.backup(dest_conn, pages=100)
    dest_conn.close()

    # Query record counts from source
    cur = src_conn.cursor()
    cur.execute("SELECT count(*) FROM observations")
    obs_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM evidence_ledger")
    ev_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM research_memos")
    memos_count = cur.fetchone()[0]
    src_conn.close()

    # 2. Backup DuckDB and Parquet datasets if present
    artifacts: Dict[str, Dict[str, Any]] = {}
    artifacts["atlas.db"] = {
        "sha256": compute_sha256(dest_sqlite),
        "size_bytes": dest_sqlite.stat().st_size
    }

    if DUCKDB_PATH.exists():
        dest_duck = backup_dir / "atlas.duckdb"
        shutil.copy2(DUCKDB_PATH, dest_duck)
        artifacts["atlas.duckdb"] = {
            "sha256": compute_sha256(dest_duck),
            "size_bytes": dest_duck.stat().st_size
        }

    # Backup Parquet
    parquet_dir = backup_dir / "processed"
    parquet_dir.mkdir(exist_ok=True)
    for p_file in PROCESSED_DATA_DIR.glob("*.parquet"):
        dest_p = parquet_dir / p_file.name
        shutil.copy2(p_file, dest_p)
        artifacts[f"processed/{p_file.name}"] = {
            "sha256": compute_sha256(dest_p),
            "size_bytes": dest_p.stat().st_size
        }

    # 3. Create manifest
    manifest = {
        "backup_id": f"BAK-{now_ts}",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sqlite_record_counts": {
            "observations": obs_count,
            "evidence_ledger": ev_count,
            "research_memos": memos_count
        },
        "artifacts": artifacts
    }

    manifest_path = backup_dir / "backup_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[+] Backup completed successfully! Manifest written to {manifest_path}")
    print(f"    Observations: {obs_count} | Evidence: {ev_count} | Memos: {memos_count}")
    return manifest_path

def verify_and_restore(manifest_path: Path, restore_target_dir: Path) -> bool:
    """Verify cryptographic integrity of backup manifest and restore into target directory."""
    print(f"[*] Verifying and restoring from {manifest_path} into {restore_target_dir}...")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    backup_dir = manifest_path.parent
    restore_target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Verify SHA-256 checksums
    for rel_path, meta in manifest["artifacts"].items():
        src_file = backup_dir / rel_path
        if not src_file.exists():
            raise FileNotFoundError(f"Missing artifact in backup: {src_file}")
        actual_sha = compute_sha256(src_file)
        if actual_sha != meta["sha256"]:
            raise ValueError(f"Checksum mismatch for {rel_path}: expected {meta['sha256']}, got {actual_sha}")
        print(f"  [OK] SHA-256 match for {rel_path} ({meta['sha256'][:12]}...)")

        # Copy to restore target
        dst_file = restore_target_dir / rel_path
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    # 2. Verify restored SQLite database integrity and table counts
    restored_db = restore_target_dir / "atlas.db"
    conn = sqlite3.connect(str(restored_db))
    cur = conn.cursor()
    # Check integrity
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    if integrity != "ok":
        raise ValueError(f"Restored database integrity check failed: {integrity}")

    cur.execute("SELECT count(*) FROM observations")
    res_obs = cur.fetchone()[0]
    conn.close()

    expected_obs = manifest["sqlite_record_counts"]["observations"]
    if res_obs != expected_obs:
        raise ValueError(f"Record count disparity in restored database: expected {expected_obs}, got {res_obs}")

    print(f"[+] Recovery verified! Integrity: OK. All {res_obs} observations verified in restored database.")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ATLAS Production Backup & Restore CLI")
    parser.add_argument("--action", choices=["backup", "restore", "test-cycle"], default="test-cycle")
    parser.add_argument("--manifest", type=str, help="Path to manifest for restore")
    parser.add_argument("--target", type=str, default="data_restored", help="Target directory for restore")

    args = parser.parse_args()

    if args.action == "backup":
        create_backup()
    elif args.action == "restore":
        if not args.manifest:
            print("Error: --manifest required for restore action")
            sys.exit(1)
        verify_and_restore(Path(args.manifest), Path(args.target))
    elif args.action == "test-cycle":
        manifest_p = create_backup()
        verify_and_restore(manifest_p, Path("backups/test_restore_verification"))
        print("[+] Full online backup and recovery test cycle PASSED.")

