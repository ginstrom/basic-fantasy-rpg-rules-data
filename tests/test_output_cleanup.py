"""Cleanup-phase normalization tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, "src")

from parsers.data_validation import normalize_data_files
from parsers.output_cleanup import cleanup_payload


def test_weapon_category_propagation() -> None:
    payload = [
        {"weapon": "Axes", "price": "", "size": "", "weight": "", "dmg": ""},
        {"weapon": "Hand Axe", "price": "4 gp", "size": "S", "weight": "5", "dmg": "1d6"},
        {"weapon": "Bows", "price": "", "size": "", "weight": "", "dmg": ""},
        {"weapon": "Shortbow", "price": "25 gp", "size": "M", "weight": "2", "dmg": ""},
    ]

    cleaned = cleanup_payload("weapons", payload)
    assert isinstance(cleaned, list)
    assert len(cleaned) == 2
    assert cleaned[0]["category"] == "Axes"
    assert cleaned[0]["weapon"] == "Hand Axe"
    assert cleaned[1]["category"] == "Bows"
    assert cleaned[1]["weapon"] == "Shortbow"


def test_range_and_comma_numeric_normalization() -> None:
    payload = {
        "level": "1-3",
        "percentile": "98-00",
        "xp": "1,225",
        "dice": "1d6",
        "threshold": "8+",
    }

    cleaned = cleanup_payload("sample", payload)
    assert cleaned["level"] == [1, 2, 3]
    assert cleaned["percentile"] == [98, 99, 100]
    assert cleaned["xp"] == 1225
    assert cleaned["dice"] == "1d6"
    assert cleaned["threshold"] == "8+"


def test_normalize_data_files_integration() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        weapons_path = root / "weapons.json"
        class_path = root / "class_tables.json"

        weapons_path.write_text(
            json.dumps(
                [
                    {"weapon": "Swords", "price": "", "size": "", "weight": "", "dmg": ""},
                    {"weapon": "Shortsword", "price": "6 gp", "size": "S", "weight": "3", "dmg": "1d6"},
                ]
            ),
            encoding="utf-8",
        )
        class_path.write_text(
            json.dumps({"fighter": [{"level": "1-2", "points": "2,000"}]}),
            encoding="utf-8",
        )

        changed = normalize_data_files(str(root))
        assert "weapons.json" in changed
        assert "class_tables.json" in changed

        weapons = json.loads(weapons_path.read_text(encoding="utf-8"))
        class_tables = json.loads(class_path.read_text(encoding="utf-8"))

        assert weapons == [
            {
                "weapon": "Shortsword",
                "price": "6 gp",
                "size": "S",
                "weight": "3",
                "dmg": "1d6",
                "category": "Swords",
            }
        ]
        assert class_tables["fighter"][0]["level"] == [1, 2]
        assert class_tables["fighter"][0]["points"] == 2000


def main() -> int:
    tests = [
        ("weapon_category_propagation", test_weapon_category_propagation),
        ("range_and_comma_numeric_normalization", test_range_and_comma_numeric_normalization),
        ("normalize_data_files_integration", test_normalize_data_files_integration),
    ]
    failed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"[PASS] {name}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {name}: {e}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
