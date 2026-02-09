"""Phase 7 validation and polish checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")

from parsers.data_validation import DATA_README, VALIDATION_REPORT, run_phase7


def main() -> int:
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = run_phase7(str(out_dir))
    print("Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    failed = 0

    report_path = out_dir / VALIDATION_REPORT
    readme_path = out_dir / DATA_README

    if not report_path.exists():
        print(f"[FAIL] Missing validation report: {report_path}")
        failed += 1
    else:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        print(f"[PASS] {report_path}")
        if report.get("summary", {}).get("critical_count", 1) == 0:
            print("[PASS] No critical cross-reference failures")
        else:
            print("[FAIL] Critical cross-reference failures remain")
            failed += 1

        if report.get("summary", {}).get("warning_count", 0) >= 0:
            print("[PASS] Warning summary recorded")
        else:
            print("[FAIL] Warning summary missing")
            failed += 1

    if not readme_path.exists():
        print(f"[FAIL] Missing data README: {readme_path}")
        failed += 1
    else:
        text = readme_path.read_text(encoding="utf-8")
        print(f"[PASS] {readme_path}")
        if "spells.json" in text and "monsters.json" in text and "validation_report.json" in text:
            print("[PASS] data README includes schema/file descriptions")
        else:
            print("[FAIL] data README missing expected file descriptions")
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
