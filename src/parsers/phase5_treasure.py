"""Phase 5 parser: treasure and magic items."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import Tag

from column_splitter import elements_between_parts
from extract_text import (
    get_section_header_text,
    get_text,
    is_section_header,
    iter_elements,
    load_html,
    table_to_rows,
)

OUTPUT_FILES = {
    "treasure_types": "treasure_types.json",
    "magic_items": "magic_items.json",
    "magic_item_tables": "magic_item_tables.json",
}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _collect_part7_blocks(elements: list[Tag]) -> list[tuple[str, list[Tag]]]:
    part7 = elements_between_parts(elements, 7, 8)
    blocks: list[tuple[str, list[Tag]]] = []
    current_header: str | None = None
    current_body: list[Tag] = []

    for el in part7:
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


def _table_from_block(block: list[Tag]) -> list[list[str]]:
    for el in block:
        if el.name == "table":
            return table_to_rows(el)
    return []


def _table_to_payload(rows: list[list[str]]) -> dict[str, object]:
    if not rows:
        return {"headers": [], "rows": []}
    headers = rows[0]
    data_rows = [r for r in rows[1:] if any(c.strip() for c in r)]
    return {"headers": headers, "rows": data_rows}


def parse_treasure_types(blocks: list[tuple[str, list[Tag]]]) -> dict[str, object]:
    target_names = ["Lair Treasures", "Individual Treasures", "Unguarded Treasures"]
    out: dict[str, object] = {}
    seen: set[str] = set()

    for name, body in blocks:
        if name not in target_names or name in seen:
            continue
        rows = _table_from_block(body)
        out[name] = _table_to_payload(rows)
        seen.add(name)

    return out


def parse_magic_item_tables(blocks: list[tuple[str, list[Tag]]]) -> list[dict[str, object]]:
    table_sections = {
        "Magic Item Generation",
        "Magic Weapons",
        "Magic Armor",
        "Potions",
        "Scrolls",
        "Wands, Staves and Rods",
        "Miscellaneous Items",
        "Miscellaneous Item Effects",
        "Rare Items",
        "Devices of Summoning Elementals",
    }

    out: list[dict[str, object]] = []
    for name, body in blocks:
        if name not in table_sections:
            continue
        for el in body:
            if el.name != "table":
                continue
            rows = table_to_rows(el)
            if not rows:
                continue
            payload = _table_to_payload(rows)
            out.append(
                {
                    "section": name,
                    "headers": payload["headers"],
                    "rows": payload["rows"],
                }
            )

    return out


def parse_magic_items(blocks: list[tuple[str, list[Tag]]]) -> list[dict[str, object]]:
    categories = {
        "Magic Weapons",
        "Magic Armor",
        "Potions",
        "Scrolls",
        "Wands, Staves and Rods",
        "Miscellaneous Item Effects",
        "Rare Items",
        "Devices of Summoning Elementals",
    }

    # Use the detailed section set after "Using Magic Items".
    start_collecting = False
    entries: list[dict[str, object]] = []

    for name, body in blocks:
        if name == "Using Magic Items":
            start_collecting = True
            continue
        if not start_collecting or name not in categories:
            continue

        current: dict[str, object] | None = None
        for el in body:
            if el.name != "p":
                continue
            txt = _norm(get_text(el))
            if not txt:
                continue

            m = re.match(r"^([^:]{2,120}):\s*(.+)$", txt)
            if m:
                if current is not None:
                    current["description"] = "\n\n".join(current["description_paragraphs"])
                    entries.append(current)
                item_name = _norm(m.group(1))
                first_para = _norm(m.group(2))
                current = {
                    "name": item_name,
                    "category": name,
                    "description_paragraphs": [first_para] if first_para else [],
                    "warnings": [],
                }
            elif current is not None:
                current["description_paragraphs"].append(txt)

        if current is not None:
            current["description"] = "\n\n".join(current["description_paragraphs"])
            entries.append(current)

    return entries


def parse_phase5_data() -> dict[str, object]:
    soup = load_html()
    elements = list(iter_elements(soup))
    blocks = _collect_part7_blocks(elements)

    return {
        "treasure_types": parse_treasure_types(blocks),
        "magic_item_tables": parse_magic_item_tables(blocks),
        "magic_items": parse_magic_items(blocks),
    }


def write_phase5_outputs(output_dir: str = "data") -> dict[str, int]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_phase5_data()
    counts: dict[str, int] = {}

    for key, filename in OUTPUT_FILES.items():
        path = out_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(parsed[key], f, indent=2, ensure_ascii=False)
            f.write("\n")

        value = parsed[key]
        if isinstance(value, dict):
            counts[key] = sum(len(v.get("rows", [])) for v in value.values() if isinstance(v, dict))
        elif isinstance(value, list):
            counts[key] = len(value)
        else:
            counts[key] = 0

    return counts


if __name__ == "__main__":
    summary = write_phase5_outputs()
    for k, v in summary.items():
        print(f"{k}: {v}")
