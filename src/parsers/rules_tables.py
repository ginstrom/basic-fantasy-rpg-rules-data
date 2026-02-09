"""Phase 2 parser: structured core rule tables.

Generates normalized JSON payloads for:
- equipment tables (weapons, armor, gear, vehicles)
- class progression tables
- saving throw tables
- thief abilities
- attack bonus table (irregular text layout)
- turning undead table
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import Tag

from section_navigation import elements_between, find_section
from extract_text import (
    get_text,
    get_text_preserve_whitespace,
    iter_elements,
    load_html,
    table_to_rows,
)

OUTPUT_FILES = {
    "weapons": "weapons.json",
    "armor": "armor.json",
    "equipment": "equipment.json",
    "vehicles": "vehicles.json",
    "class_tables": "class_tables.json",
    "saving_throws": "saving_throws.json",
    "thief_abilities": "thief_abilities.json",
    "attack_bonus": "attack_bonus.json",
    "turning_undead": "turning_undead.json",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _rows_to_records(rows: list[list[str]]) -> list[dict[str, str]]:
    if len(rows) < 2:
        return []
    headers = [_slug(h) for h in rows[0]]
    out: list[dict[str, str]] = []
    for row in rows[1:]:
        if not any(c.strip() for c in row):
            continue
        rec: dict[str, str] = {}
        for i, key in enumerate(headers):
            if not key:
                key = f"column_{i + 1}"
            rec[key] = row[i] if i < len(row) else ""
        out.append(rec)
    return out


def _find_first_table_in_section(elements: list[Tag], header: str) -> list[list[str]]:
    for el in elements_between(elements, header):
        if el.name == "table":
            return table_to_rows(el)
    return []


def _find_tables_in_section(elements: list[Tag], header: str) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    for el in elements_between(elements, header):
        if el.name == "table":
            tables.append(table_to_rows(el))
    return tables


def parse_weapons(elements: list[Tag]) -> list[dict[str, str]]:
    rows = _find_first_table_in_section(elements, "Weapons")
    return _rows_to_records(rows)


def parse_armor(elements: list[Tag]) -> list[dict[str, str]]:
    rows = _find_first_table_in_section(elements, "Armor and Shields")
    return _rows_to_records(rows)


def parse_equipment(elements: list[Tag]) -> list[dict[str, str]]:
    tables = _find_tables_in_section(elements, "Equipment")
    out: list[dict[str, str]] = []
    for rows in tables:
        out.extend(_rows_to_records(rows))
    return out


def parse_vehicles(elements: list[Tag]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    section_map = {
        "Land Transportation": "land",
        "Water Transportation": "water",
    }
    for header, category in section_map.items():
        rows = _find_first_table_in_section(elements, header)
        for rec in _rows_to_records(rows):
            rec["category"] = category
            out.append(rec)
    return out


def parse_class_tables(elements: list[Tag]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for class_name in ["Cleric", "Fighter", "Magic-User"]:
        rows = _find_first_table_in_section(elements, class_name)
        if not rows:
            continue

        # Normalize two-row header variants like ["", "Exp.", "", "Spells"] +
        # ["Level", "Points", "Hit Dice", "1", ...]
        headers: list[str]
        if len(rows) > 1 and rows[0] and rows[1] and rows[0][0] == "":
            merged = []
            width = max(len(rows[0]), len(rows[1]))
            for i in range(width):
                a = rows[0][i] if i < len(rows[0]) else ""
                b = rows[1][i] if i < len(rows[1]) else ""
                merged.append(b or a)
            headers = [_slug(h) for h in merged]
            data_rows = rows[2:]
        else:
            headers = [_slug(h) for h in rows[0]]
            data_rows = rows[1:]

        records: list[dict[str, str]] = []
        for row in data_rows:
            if not row or not any(cell.strip() for cell in row):
                continue
            rec: dict[str, str] = {}
            for i, key in enumerate(headers):
                if not key:
                    key = f"column_{i + 1}"
                rec[key] = row[i] if i < len(row) else ""
            records.append(rec)

        out[_slug(class_name)] = records
    return out


def parse_saving_throws(elements: list[Tag]) -> dict[str, list[dict[str, str]]]:
    section = elements_between(elements, "Saving Throw Tables by Class")
    out: dict[str, list[dict[str, str]]] = {}

    current_class = ""
    for el in section:
        if el.name == "p":
            t = get_text(el)
            if t in {"Cleric", "Fighter", "Magic-User", "Thief"}:
                current_class = _slug(t)
        elif el.name == "table" and current_class:
            rows = table_to_rows(el)
            out[current_class] = _rows_to_records(rows)
            current_class = ""
    return out


def parse_thief_abilities(elements: list[Tag]) -> list[dict[str, str]]:
    rows = _find_first_table_in_section(elements, "Thief Abilities")
    return _rows_to_records(rows)


def parse_attack_bonus(elements: list[Tag]) -> list[dict[str, str]]:
    idx = find_section(elements, "Attack Bonus Table")
    if idx is None:
        return []

    text = get_text_preserve_whitespace(elements[idx])
    block = text.split('To roll "to hit,"', 1)[0]
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in block.splitlines()]
    lines = [ln for ln in lines if ln]

    try:
        start = lines.index("NM")
    except ValueError:
        return []

    tokens = lines[start:]
    out: list[dict[str, str]] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        if tok == "NM":
            if i + 2 >= len(tokens):
                break
            out.append(
                {
                    "fighter_level": "NM",
                    "cleric_or_thief_level": "",
                    "magic_user_level": "",
                    "monster_hit_dice": tokens[i + 1],
                    "attack_bonus": tokens[i + 2],
                }
            )
            i += 3
            continue

        if re.fullmatch(r"\+\d+", tok):
            # malformed ordering; stop rather than inventing data
            break

        # Gather fields until the bonus marker (e.g. +7)
        fields: list[str] = []
        while i < len(tokens) and not re.fullmatch(r"\+\d+", tokens[i]):
            fields.append(tokens[i])
            i += 1
        if i >= len(tokens):
            break

        bonus = tokens[i]
        i += 1

        rec = {
            "fighter_level": "",
            "cleric_or_thief_level": "",
            "magic_user_level": "",
            "monster_hit_dice": "",
            "attack_bonus": bonus,
        }

        # Layout is irregular at high levels; map by observed field count.
        if len(fields) == 4:
            rec["fighter_level"], rec["cleric_or_thief_level"], rec["magic_user_level"], rec["monster_hit_dice"] = fields
        elif len(fields) == 3:
            rec["fighter_level"], rec["cleric_or_thief_level"], rec["monster_hit_dice"] = fields
        elif len(fields) == 2:
            rec["fighter_level"], rec["monster_hit_dice"] = fields
        elif len(fields) == 1:
            rec["monster_hit_dice"] = fields[0]
        else:
            continue

        out.append(rec)

    return out


def parse_turning_undead(soup) -> dict[str, object]:
    for table in soup.find_all("table"):
        rows = table_to_rows(table)
        if not rows:
            continue
        header = rows[0]
        if header and header[0] == "Cleric Level" and "Skeleton" in header:
            hd_row = rows[1] if len(rows) > 1 else []
            data = rows[2:]
            records = []
            for row in data:
                if not row or not row[0].strip():
                    continue
                rec: dict[str, str] = {"cleric_level": row[0]}
                for i, undead in enumerate(header[1:], start=1):
                    rec[_slug(undead)] = row[i] if i < len(row) else ""
                records.append(rec)
            return {
                "undead_columns": [
                    {
                        "name": header[i],
                        "hit_dice": hd_row[i - 1] if i - 1 < len(hd_row) else "",
                    }
                    for i in range(1, len(header))
                ],
                "rows": records,
            }
    return {"undead_columns": [], "rows": []}


def parse_phase2_data() -> dict[str, object]:
    soup = load_html()
    elements = list(iter_elements(soup))

    return {
        "weapons": parse_weapons(elements),
        "armor": parse_armor(elements),
        "equipment": parse_equipment(elements),
        "vehicles": parse_vehicles(elements),
        "class_tables": parse_class_tables(elements),
        "saving_throws": parse_saving_throws(elements),
        "thief_abilities": parse_thief_abilities(elements),
        "attack_bonus": parse_attack_bonus(elements),
        "turning_undead": parse_turning_undead(soup),
    }


def write_phase2_outputs(output_dir: str = "data") -> dict[str, int]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_phase2_data()
    counts: dict[str, int] = {}

    for key, filename in OUTPUT_FILES.items():
        value = parsed[key]
        path = out_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
            f.write("\n")

        if isinstance(value, list):
            counts[key] = len(value)
        elif isinstance(value, dict):
            # count first-class records for reporting
            if key == "turning_undead":
                counts[key] = len(value.get("rows", []))
            else:
                counts[key] = sum(len(v) for v in value.values() if isinstance(v, list))
        else:
            counts[key] = 0

    return counts


if __name__ == "__main__":
    summary = write_phase2_outputs()
    for name in OUTPUT_FILES:
        print(f"{name}: {summary.get(name, 0)}")
