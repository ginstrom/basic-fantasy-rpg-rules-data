"""Phase 3 spell output validation.

Run with:
    .venv/bin/python tests/test_spells.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.spells import OUTPUT_FILES, write_phase3_outputs


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    counts = write_phase3_outputs(str(out_dir))
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
            json.loads(path.read_text(encoding="utf-8"))
            print(f"[PASS] {path}")
        except json.JSONDecodeError as e:
            print(f"[FAIL] Invalid JSON in {path}: {e}")
            failed += 1

    spells = json.loads((out_dir / OUTPUT_FILES["spells"]).read_text(encoding="utf-8"))
    spell_list = json.loads((out_dir / OUTPUT_FILES["spell_list"]).read_text(encoding="utf-8"))

    if 90 <= len(spells) <= 110:
        print(f"[PASS] Spell count in expected range: {len(spells)}")
    else:
        print(f"[FAIL] Spell count out of range: {len(spells)}")
        failed += 1

    missing_meta = [s["name"] for s in spells if not s.get("class_levels")]
    if not missing_meta:
        print("[PASS] All spells include class/level metadata")
    else:
        print(f"[FAIL] Spells missing class_levels: {missing_meta[:8]}")
        failed += 1

    reversible = [s for s in spells if s.get("reversible")]
    if reversible:
        print(f"[PASS] Reversible spells detected: {len(reversible)}")
    else:
        print("[FAIL] No reversible spells detected")
        failed += 1

    embedded_tables = sum(len(s.get("embedded_tables", [])) for s in spells)
    if embedded_tables >= 2:
        print(f"[PASS] Embedded spell tables extracted: {embedded_tables}")
    else:
        print(f"[FAIL] Expected embedded tables, found: {embedded_tables}")
        failed += 1

    listed = {row["name_clean"] for row in spell_list.get("spell_levels", [])}
    parsed = {s["name_clean"] for s in spells}
    overlap = len(listed & parsed)
    if overlap >= 60:
        print(f"[PASS] Spell list overlap with parsed entries: {overlap}")
    else:
        print(f"[FAIL] Spell list overlap too small: {overlap}")
        failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
