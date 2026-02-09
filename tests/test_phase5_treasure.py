"""Phase 5 treasure/magic item output validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.phase5_treasure import OUTPUT_FILES, write_phase5_outputs


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = write_phase5_outputs(str(out_dir))
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

    treasure = loaded.get("treasure_types", {})
    for key in ["Lair Treasures", "Individual Treasures", "Unguarded Treasures"]:
        rows = treasure.get(key, {}).get("rows", [])
        if rows:
            print(f"[PASS] Treasure table present: {key} ({len(rows)} rows)")
        else:
            print(f"[FAIL] Missing/empty treasure table: {key}")
            failed += 1

    item_tables = loaded.get("magic_item_tables", [])
    if len(item_tables) >= 12:
        print(f"[PASS] Magic item tables extracted: {len(item_tables)}")
    else:
        print(f"[FAIL] Too few magic item tables: {len(item_tables)}")
        failed += 1

    items = loaded.get("magic_items", [])
    if len(items) >= 60:
        print(f"[PASS] Magic item entries extracted: {len(items)}")
    else:
        print(f"[FAIL] Too few magic item entries: {len(items)}")
        failed += 1

    missing_desc = [x["name"] for x in items if not x.get("description")]
    if not missing_desc:
        print("[PASS] All magic item entries have descriptions")
    else:
        print(f"[FAIL] Magic item entries missing descriptions: {missing_desc[:8]}")
        failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
