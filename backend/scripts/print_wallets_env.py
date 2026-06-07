"""Print WALLETS_JSON for pasting into Render env vars."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

if not config.WALLETS_PATH.exists():
    sys.exit(f"Missing {config.WALLETS_PATH}")

data = json.loads(config.WALLETS_PATH.read_text())
print(json.dumps(data, separators=(",", ":")))
