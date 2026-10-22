import os
from pathlib import Path

DATA_DIR = Path(os.environ.get(
    "INFLUENCER_DATA_DIR",
    Path.home() / "Desktop" / "influencer-data" / "_derived",
))
ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"
