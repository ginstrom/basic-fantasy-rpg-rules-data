"""Phase 6 parser: races, classes, encounters, and combat references."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import Tag

from section_navigation import elements_between_parts
from extract_text import (
    get_section_header_text,
    get_text,
    is_section_header,
    iter_elements,
    load_html,
    table_to_rows,
)

OUTPUT_FILES = {
    "races": "races.json",
    "classes": "classes.json",
    "encounter_tables": "encounter_tables.json",
    "combat_tables": "combat_tables.json",
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _collect_blocks(elements: list[Tag], start_part: int, end_part: int) -> list[tuple[str, list[Tag]]]:
    seg = elements_between_parts(elements, start_part, end_part)
    blocks: list[tuple[str, list[Tag]]] = []
    current_header: str | None = None
    current_body: list[Tag] = []

    for el in seg:
        if is_section_header(el):
            if current_header is not None:
                blocks.append((current_header, current_body))
            current_header = get_section_header_text(el) or ""
            current_body = []
        else:
            current_body.append(el)

    if current_header is not None:
        blocks.append((current_header, current_body))
    return blocks


def _extract_paragraphs(body: list[Tag]) -> list[str]:
    return [_norm(get_text(el)) for el in body if el.name == "p" and _norm(get_text(el))]


def _extract_labeled_fields(paragraphs: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for p in paragraphs:
        m = re.match(r"^([^:]{2,40}):\s*(.+)$", p)
        if not m:
            continue
        key = _slug(m.group(1))
        fields[key] = _norm(m.group(2))
    return fields


def parse_races(part2_blocks: list[tuple[str, list[Tag]]]) -> list[dict[str, object]]:
    race_names = ["Dwarves", "Elves", "Halflings", "Humans"]
    out = []
    for name, body in part2_blocks:
        if name not in race_names:
            continue
        paragraphs = _extract_paragraphs(body)
        out.append(
            {
                "name": name,
                "fields": _extract_labeled_fields(paragraphs),
                "description_paragraphs": paragraphs,
                "description": "\n\n".join(paragraphs),
            }
        )
    return out


def parse_classes(part2_blocks: list[tuple[str, list[Tag]]]) -> list[dict[str, object]]:
    class_names = ["Cleric", "Fighter", "Magic-User", "Thief"]
    out = []
    for name, body in part2_blocks:
        if name not in class_names:
            continue
        paragraphs = _extract_paragraphs(body)
        out.append(
            {
                "name": name,
                "fields": _extract_labeled_fields(paragraphs),
                "description_paragraphs": paragraphs,
                "description": "\n\n".join(paragraphs),
            }
        )
    return out


def parse_encounters(part8_blocks: list[tuple[str, list[Tag]]]) -> dict[str, list[dict[str, object]]]:
    out = {"dungeon": [], "wilderness": []}

    for name, body in part8_blocks:
        if name not in {"Dungeon Encounters", "Wilderness Encounters"}:
            continue
        key = "dungeon" if name == "Dungeon Encounters" else "wilderness"
        table_idx = 0
        for el in body:
            if el.name != "table":
                continue
            rows = table_to_rows(el)
            if not rows:
                continue
            table_idx += 1
            out[key].append(
                {
                    "table_name": f"{name} #{table_idx}",
                    "source_section": name,
                    "headers": rows[0],
                    "rows": [r for r in rows[1:] if any(c.strip() for c in r)],
                }
            )

    return out


def _load_json_if_exists(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def parse_combat_tables(part2_blocks: list[tuple[str, list[Tag]]], part5_blocks: list[tuple[str, list[Tag]]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []

    wanted_part2 = {"Missile Weapon Ranges", "Siege Engines"}
    for name, body in part2_blocks:
        if name not in wanted_part2:
            continue
        for el in body:
            if el.name != "table":
                continue
            rows = table_to_rows(el)
            if not rows:
                continue
            out.append(
                {
                    "table_name": name,
                    "source_section": name,
                    "source_part": 2,
                    "headers": rows[0],
                    "rows": [r for r in rows[1:] if any(c.strip() for c in r)],
                }
            )

    # Part 5 reaction table
    for name, body in part5_blocks:
        if name != "Monster Reactions":
            continue
        for el in body:
            if el.name != "table":
                continue
            rows = table_to_rows(el)
            if not rows:
                continue
            out.append(
                {
                    "table_name": name,
                    "source_section": name,
                    "source_part": 5,
                    "headers": rows[0],
                    "rows": [r for r in rows[1:] if any(c.strip() for c in r)],
                }
            )

    # Reuse phase-2 derived combat references when available.
    attack_bonus = _load_json_if_exists(Path("data/attack_bonus.json"))
    if isinstance(attack_bonus, list) and attack_bonus:
        headers = list(attack_bonus[0].keys())
        rows = [[str(rec.get(h, "")) for h in headers] for rec in attack_bonus]
        out.append(
            {
                "table_name": "Attack Bonus Table",
                "source_section": "How to Attack",
                "source_part": 5,
                "headers": headers,
                "rows": rows,
            }
        )

    saving_throws = _load_json_if_exists(Path("data/saving_throws.json"))
    if isinstance(saving_throws, dict) and saving_throws:
        for cls, records in saving_throws.items():
            if not records:
                continue
            headers = list(records[0].keys())
            rows = [[str(rec.get(h, "")) for h in headers] for rec in records]
            out.append(
                {
                    "table_name": f"Saving Throws ({cls})",
                    "source_section": "Saving Throw Tables by Class",
                    "source_part": 5,
                    "headers": headers,
                    "rows": rows,
                }
            )

    return out


def parse_phase6_data() -> dict[str, object]:
    soup = load_html()
    elements = list(iter_elements(soup))

    part2_blocks = _collect_blocks(elements, 2, 3)
    part5_blocks = _collect_blocks(elements, 5, 6)
    part8_blocks = _collect_blocks(elements, 8, 9)

    return {
        "races": parse_races(part2_blocks),
        "classes": parse_classes(part2_blocks),
        "encounter_tables": parse_encounters(part8_blocks),
        "combat_tables": parse_combat_tables(part2_blocks, part5_blocks),
    }


def write_phase6_outputs(output_dir: str = "data") -> dict[str, int]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_phase6_data()
    counts: dict[str, int] = {}

    for key, filename in OUTPUT_FILES.items():
        path = out_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(parsed[key], f, indent=2, ensure_ascii=False)
            f.write("\n")

        value = parsed[key]
        if isinstance(value, list):
            counts[key] = len(value)
        elif isinstance(value, dict):
            counts[key] = sum(len(v) for v in value.values() if isinstance(v, list))
        else:
            counts[key] = 0

    return counts


if __name__ == "__main__":
    summary = write_phase6_outputs()
    for k, v in summary.items():
        print(f"{k}: {v}")
