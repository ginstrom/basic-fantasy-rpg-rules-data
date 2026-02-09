"""Phase 4 monster output validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.monsters import OUTPUT_FILE, write_phase4_output


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = write_phase4_output(str(out_dir))
    print("Generated:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    failed = 0
    path = out_dir / OUTPUT_FILE
    if not path.exists():
        print(f"[FAIL] Missing file: {path}")
        return 1

    try:
        monsters = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"[FAIL] Invalid JSON: {e}")
        return 1

    print(f"[PASS] {path}")

    if len(monsters) >= 200:
        print(f"[PASS] Monster count in expected range: {len(monsters)}")
    else:
        print(f"[FAIL] Monster count too low: {len(monsters)}")
        failed += 1

    with_core = 0
    for m in monsters:
        stat = m.get("stat_block", {})
        if stat.get("armor_class") and stat.get("hit_dice") and stat.get("xp"):
            with_core += 1

    if with_core >= 180:
        print(f"[PASS] Core stat coverage looks good: {with_core}")
    else:
        print(f"[FAIL] Core stat coverage too low: {with_core}")
        failed += 1

    cross_refs = [m for m in monsters if "cross_reference_only" in m.get("warnings", [])]
    if cross_refs:
        print(f"[PASS] Cross-reference-only entries captured: {len(cross_refs)}")
    else:
        print("[FAIL] No cross-reference-only entries captured")
        failed += 1

    dragon_tables = sum(len(m.get("dragon_age_tables", [])) for m in monsters)
    if dragon_tables >= 8:
        print(f"[PASS] Dragon age tables captured: {dragon_tables}")
    else:
        print(f"[FAIL] Dragon age tables missing/incomplete: {dragon_tables}")
        failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
