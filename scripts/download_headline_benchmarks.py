"""Script to download and verify official evaluation splits for the headline research benchmarks:
1. T²-RAGBench (Text-and-Table Financial RAG Benchmark)
2. FinanceMath (Knowledge-Intensive Financial Math Reasoning)
3. AVeriTeC (Real-World Automated Claim Verification with Evidence from the Web)
"""

import os
import sys
import json
import shutil
import hashlib
import urllib.request
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BENCHMARKS_DIR = PROJECT_ROOT / "data" / "benchmarks"
BENCHMARKS_DIR.mkdir(parents=True, exist_ok=True)

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def download_financemath():
    print("[1/3] Downloading FinanceMath official splits...")
    files = {
        "financemath_validation.json": "https://raw.githubusercontent.com/yale-nlp/FinanceMath/main/data/validation.json",
        "financemath_test.json": "https://raw.githubusercontent.com/yale-nlp/FinanceMath/main/data/test.json"
    }
    results = {}
    for filename, url in files.items():
        dest = BENCHMARKS_DIR / filename
        if not dest.exists() or dest.stat().st_size == 0:
            print(f"  Downloading {filename} from {url}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ATLAS Research Workbench)"})
            with urllib.request.urlopen(req) as resp, open(dest, "wb") as f:
                shutil.copyfileobj(resp, f)
        
        with open(dest, "r", encoding="utf-8") as f:
            data = json.load(f)
        sha = compute_sha256(dest)
        print(f"  [OK] {filename}: {len(data)} items | SHA-256: {sha[:12]}...")
        results[filename] = {"count": len(data), "sha256": sha}
    return results

def download_averitec():
    print("[2/3] Downloading AVeriTeC official splits...")
    from huggingface_hub import hf_hub_download
    results = {}
    for split_name, hf_file, local_name in [
        ("dev", "data/dev-00000-of-00001.parquet", "averitec_dev.parquet"),
        ("train", "data/train-00000-of-00001.parquet", "averitec_train.parquet")
    ]:
        dest = BENCHMARKS_DIR / local_name
        if not dest.exists() or dest.stat().st_size == 0:
            print(f"  Downloading AVeriTeC {split_name} ({hf_file})...")
            p = hf_hub_download("pminervini/averitec", filename=hf_file, repo_type="dataset")
            shutil.copy2(p, dest)

        df = pd.read_parquet(dest)
        sha = compute_sha256(dest)
        print(f"  [OK] {local_name}: {len(df)} claims | Columns: {len(df.columns)} | SHA-256: {sha[:12]}...")
        results[local_name] = {"count": len(df), "sha256": sha}
    return results

def download_t2_ragbench():
    print("[3/3] Downloading T²-RAGBench official evaluation splits...")
    from huggingface_hub import hf_hub_download
    results = {}
    for config_name, hf_file, local_name in [
        ("TAT-DQA dev", "data/TAT-DQA/dev/metadata.jsonl", "t2_ragbench_tatdqa_dev.jsonl"),
        ("TAT-DQA test", "data/TAT-DQA/test/metadata.jsonl", "t2_ragbench_tatdqa_test.jsonl"),
        ("FinQA dev", "data/FinQA/dev/metadata.jsonl", "t2_ragbench_finqa_dev.jsonl")
    ]:
        dest = BENCHMARKS_DIR / local_name
        if not dest.exists() or dest.stat().st_size == 0:
            print(f"  Downloading T²-RAGBench {config_name} ({hf_file})...")
            p = hf_hub_download("G4KMU/t2-ragbench", filename=hf_file, repo_type="dataset")
            shutil.copy2(p, dest)

        with open(dest, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        sha = compute_sha256(dest)
        print(f"  [OK] {local_name}: {len(lines)} samples | SHA-256: {sha[:12]}...")
        results[local_name] = {"count": len(lines), "sha256": sha}
    return results

def main():
    print("=" * 70)
    print("  DOWNLOADING & VERIFYING HEADLINE BENCHMARKS")
    print("=" * 70)
    fm = download_financemath()
    av = download_averitec()
    t2 = download_t2_ragbench()

    manifest = {
        "download_timestamp_utc": pd.Timestamp.now("UTC").isoformat(),
        "benchmarks": {
            "FinanceMath": fm,
            "AVeriTeC": av,
            "T2-RAGBench": t2
        }
    }
    manifest_p = BENCHMARKS_DIR / "headline_benchmarks_manifest.json"
    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n[+] All headline benchmark splits downloaded and verified. Manifest: {manifest_p}")

if __name__ == "__main__":
    main()

