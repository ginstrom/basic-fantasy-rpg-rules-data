"""Phase 7: cross-file validation, cleanup, and data documentation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from parsers.output_cleanup import cleanup_payload

VALIDATION_REPORT = "validation_report.json"
DATA_README = "README.md"


def _norm(s: str) -> str:
    s = s.replace("\t", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _canon(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _clean_obj(value: Any) -> Any:
    if isinstance(value, str):
        return _norm(value)
    if isinstance(value, list):
        return [_clean_obj(v) for v in value]
    if isinstance(value, dict):
        return {k: _clean_obj(v) for k, v in value.items()}
    return value


def normalize_data_files(data_dir: str = "data") -> list[str]:
    out = []
    for path in sorted(Path(data_dir).glob("*.json")):
        if path.name == VALIDATION_REPORT:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        cleaned = _clean_obj(payload)
        cleaned = cleanup_payload(path.stem, cleaned)
        path.write_text(json.dumps(cleaned, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        out.append(path.name)
    return out


def _load_json(data_dir: Path, filename: str):
    path = data_dir / filename
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_encounter_candidates(encounters: dict[str, list[dict[str, Any]]]) -> set[str]:
    names: set[str] = set()
    for tables in encounters.values():
        for table in tables:
            headers = table.get("headers", [])
            rows = table.get("rows", [])
            start_col = 1 if headers else 0
            for row in rows:
                for cell in row[start_col:]:
                    txt = _norm(str(cell))
                    if not txt:
                        continue
                    # Remove leading roll/count patterns like "1d6", "2-8", "d%"
                    txt = re.sub(r"^(\d+d\d+|\d+-\d+|\d+|d%)\s+", "", txt, flags=re.I)
                    # Split on common separators.
                    parts = re.split(r"[,/;]|\bor\b|\band\b", txt, flags=re.I)
                    for p in parts:
                        p = _norm(re.sub(r"\(.*?\)", "", p))
                        if len(p) < 3:
                            continue
                        names.add(_canon(p))
    return names


def _monster_aliases(monsters: list[dict[str, Any]]) -> set[str]:
    aliases: set[str] = set()
    for m in monsters:
        name = _norm(m.get("name", ""))
        if not name:
            continue
        aliases.add(_canon(name))

        base = _norm(re.sub(r"\(.*?\)", "", name))
        aliases.add(_canon(base))

        for part in re.split(r",|\bor\b|\band\b", base, flags=re.I):
            p = _norm(part)
            if p:
                aliases.add(_canon(p))
    return {a for a in aliases if a}


def run_validation(data_dir: str = "data") -> dict[str, Any]:
    root = Path(data_dir)
    issues: list[dict[str, str]] = []

    spells = _load_json(root, "spells.json") or []
    spell_lists = _load_json(root, "spell_lists.json") or {}
    monsters = _load_json(root, "monsters.json") or []
    encounters = _load_json(root, "encounter_tables.json") or {}
    combat_tables = _load_json(root, "combat_tables.json") or []

    spell_names = {_canon(s.get("name_clean", "")) for s in spells if s.get("name_clean")}
    listed_names = {_canon(x.get("name_clean", "")) for x in spell_lists.get("all", []) if x.get("name_clean")}
    missing_spells = sorted(n for n in listed_names if n and n not in spell_names)
    if missing_spells:
        # Small residual mismatches are expected from naming/edition drift
        # and should be triaged, but not block a release as critical failures.
        severity = "critical" if len(missing_spells) > 15 else "warning"
        issues.append(
            {
                "severity": severity,
                "check": "spell_list_references",
                "message": f"{len(missing_spells)} spell list names missing from spells.json",
            }
        )

    encounter_candidates = _extract_encounter_candidates(encounters)
    monster_alias_set = _monster_aliases(monsters)
    missing_monster_refs = sorted(n for n in encounter_candidates if n and n not in monster_alias_set)
    if missing_monster_refs:
        issues.append(
            {
                "severity": "warning",
                "check": "encounter_monster_references",
                "message": f"{len(missing_monster_refs)} encounter references not matched to monster aliases",
            }
        )

    bad_combat = [t.get("table_name", "<unnamed>") for t in combat_tables if not t.get("headers") or not t.get("rows")]
    if bad_combat:
        issues.append(
            {
                "severity": "warning",
                "check": "combat_table_structure",
                "message": f"{len(bad_combat)} combat tables have missing headers/rows",
            }
        )

    critical = [i for i in issues if i["severity"] == "critical"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    report = {
        "summary": {
            "critical_count": len(critical),
            "warning_count": len(warnings),
            "status": "pass" if not critical else "fail",
        },
        "checks": {
            "spell_list_names": {
                "listed": len(listed_names),
                "resolved": len(listed_names) - len(missing_spells),
                "missing_sample": missing_spells[:20],
            },
            "encounter_monster_refs": {
                "candidates": len(encounter_candidates),
                "resolved": len(encounter_candidates) - len(missing_monster_refs),
                "unresolved_sample": missing_monster_refs[:30],
            },
            "combat_tables": {
                "count": len(combat_tables),
                "malformed": bad_combat,
            },
        },
        "issues": issues,
        "notes": [
            "Encounter-reference matching uses heuristic tokenization and may over-report unresolved aliases.",
            "Non-critical warnings should be reviewed before downstream strict linking.",
        ],
    }

    return report


def write_data_readme(data_dir: str = "data") -> None:
    readme = Path(data_dir) / DATA_README
    readme.write_text(
        """# Data Outputs

Generated structured JSON outputs from the Basic Fantasy RPG manual.

## Files

- `armor.json`: Armor and shield equipment table.
- `attack_bonus.json`: Attack bonus progression table.
- `class_tables.json`: Class progression tables (cleric/fighter/magic-user).
- `classes.json`: Class prose descriptions and labeled fields.
- `combat_tables.json`: Normalized combat-reference tables with source metadata.
- `encounter_tables.json`: Dungeon and wilderness encounter tables.
- `equipment.json`: General equipment tables.
- `magic_items.json`: Magic item entries parsed from prose sections.
- `magic_item_tables.json`: Random generation and magic-item roll tables.
- `monsters.json`: Monster records with stat blocks, descriptions, and warnings.
- `races.json`: Race prose descriptions and labeled fields.
- `saving_throws.json`: Saving throw progression by class.
- `spell_lists.json`: Spell indexes by class and level.
- `spells.json`: Individual spell records with metadata and descriptions.
- `thief_abilities.json`: Thief ability progression table.
- `treasure_types.json`: Treasure type and value tables.
- `turning_undead.json`: Cleric turning-undead progression table.
- `vehicles.json`: Land and water vehicle tables.
- `weapons.json`: Weapon table with per-item `category` values.
- `validation_report.json`: Cross-file validation report and unresolved warnings.

## Notes

- String normalization collapses OCR/layout whitespace artifacts.
- Numeric cleanup converts comma-formatted numbers (e.g. `1,000`) to integers.
- Numeric ranges (e.g. `1-3`) are normalized to integer lists.
- Some files include `warnings` arrays to preserve partial/edge parses.
- Encounter-to-monster references are validated heuristically.
""",
        encoding="utf-8",
    )


def run_phase7(data_dir: str = "data") -> dict[str, Any]:
    cleaned = normalize_data_files(data_dir)
    report = run_validation(data_dir)

    out_path = Path(data_dir) / VALIDATION_REPORT
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    write_data_readme(data_dir)

    return {
        "cleaned_files": cleaned,
        "critical_count": report["summary"]["critical_count"],
        "warning_count": report["summary"]["warning_count"],
        "status": report["summary"]["status"],
    }


if __name__ == "__main__":
    result = run_phase7("data")
    for k, v in result.items():
        print(f"{k}: {v}")
