"""Launch script for ATLAS Streamlit UI."""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent.parent / "atlas" / "frontend" / "app.py"
    print(f"Launching ATLAS Workbench UI from {app_path} on port 8501...")
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port=8501",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    subprocess.run(cmd)

