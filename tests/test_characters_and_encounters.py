"""Phase 6 output validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.characters_and_encounters import OUTPUT_FILES, write_phase6_outputs


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = write_phase6_outputs(str(out_dir))
    print("Generated:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    failed = 0
    loaded = {}
    for key, filename in OUTPUT_FILES.items():
        path = out_dir / filename
        if not path.exists():
            print(f"[FAIL] Missing file: {path}")
            failed += 1
            continue
        try:
            loaded[key] = json.loads(path.read_text(encoding="utf-8"))
            print(f"[PASS] {path}")
        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON in {path}: {e}")
            failed += 1

    races = loaded.get("races", [])
    classes = loaded.get("classes", [])
    encounters = loaded.get("encounter_tables", {})
    combat = loaded.get("combat_tables", [])

    if len(races) >= 4:
        print(f"[PASS] Race entries extracted: {len(races)}")
    else:
        print(f"[FAIL] Race entries too low: {len(races)}")
        failed += 1

    if len(classes) >= 4:
        print(f"[PASS] Class entries extracted: {len(classes)}")
    else:
        print(f"[FAIL] Class entries too low: {len(classes)}")
        failed += 1

    dungeons = encounters.get("dungeon", [])
    wilds = encounters.get("wilderness", [])
    if dungeons and wilds:
        print(f"[PASS] Encounter tables extracted (dungeon={len(dungeons)}, wilderness={len(wilds)})")
    else:
        print(f"[FAIL] Encounter table extraction incomplete (dungeon={len(dungeons)}, wilderness={len(wilds)})")
        failed += 1

    if len(combat) >= 5:
        print(f"[PASS] Combat tables extracted: {len(combat)}")
    else:
        print(f"[FAIL] Combat tables too low: {len(combat)}")
        failed += 1

    malformed = [t.get("table_name", "<unnamed>") for t in combat if not t.get("headers") or not t.get("rows")]
    if not malformed:
        print("[PASS] Combat tables are machine-readable")
    else:
        print(f"[FAIL] Malformed combat tables: {malformed[:8]}")
        failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
