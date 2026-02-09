"""Phase 2 output validation.

Checks that all required Phase 2 JSON files are generated and non-empty.

Run with:
    .venv/bin/python tests/test_phase2_tables.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.phase2_tables import OUTPUT_FILES, write_phase2_outputs


REQUIRED_NON_EMPTY = {
    "weapons",
    "armor",
    "equipment",
    "vehicles",
    "class_tables",
    "saving_throws",
    "thief_abilities",
    "attack_bonus",
    "turning_undead",
}


def _is_non_empty_payload(name: str, payload) -> bool:
    if name == "turning_undead":
        return bool(payload.get("rows")) and bool(payload.get("undead_columns"))
    if isinstance(payload, list):
        return len(payload) > 0
    if isinstance(payload, dict):
        return any(bool(v) for v in payload.values())
    return False


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    counts = write_phase2_outputs(str(out_dir))
    print("Generated:")
    for k in OUTPUT_FILES:
        print(f"  {k}: {counts.get(k, 0)}")

    failed = 0

    for key, filename in OUTPUT_FILES.items():
        path = out_dir / filename
        if not path.exists():
            print(f"[FAIL] Missing file: {path}")
            failed += 1
            continue

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON in {path}: {e}")
            failed += 1
            continue

        if key in REQUIRED_NON_EMPTY and not _is_non_empty_payload(key, payload):
            print(f"[FAIL] Empty payload in {path}")
            failed += 1
        else:
            print(f"[PASS] {path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
