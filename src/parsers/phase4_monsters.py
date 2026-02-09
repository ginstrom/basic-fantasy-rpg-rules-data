"""Phase 4 parser: monster stat blocks and descriptions."""

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

OUTPUT_FILE = "monsters.json"

CORE_FIELDS = {
    "armor_class",
    "hit_dice",
    "no_of_attacks",
    "damage",
    "movement",
    "no_appearing",
    "save_as",
    "morale",
    "treasure_type",
    "xp",
}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _is_stat_table(rows: list[list[str]]) -> bool:
    return any(r and "Armor Class:" in r[0] for r in rows)


def _is_age_table(rows: list[list[str]]) -> bool:
    return bool(rows and rows[0] and "Age Table" in rows[0][0])


def _parse_stat_rows(rows: list[list[str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in rows:
        if not row:
            continue
        label = _norm(row[0])
        if not label:
            continue
        if not label.endswith(":"):
            continue
        key = _slug(label[:-1])
        value = _norm(" | ".join(row[1:])) if len(row) > 1 else ""
        out[key] = value
    return out


def _parse_grid_table(rows: list[list[str]]) -> dict[str, object]:
    if not rows:
        return {"headers": [], "rows": []}
    headers = rows[0]
    data_rows = [r for r in rows[1:] if any(c.strip() for c in r)]
    return {"headers": headers, "rows": data_rows}


def _collect_part6_blocks(elements: list[Tag]) -> list[tuple[str, list[Tag]]]:
    part6 = elements_between_parts(elements, 6, 7)
    blocks: list[tuple[str, list[Tag]]] = []
    current_header: str | None = None
    current_body: list[Tag] = []

    for el in part6:
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


def parse_monsters(elements: list[Tag]) -> list[dict[str, object]]:
    blocks = _collect_part6_blocks(elements)
    monsters: list[dict[str, object]] = []

    for name, body in blocks:
        if name in {"PART 6: MONSTERS", "Monster Descriptions"}:
            continue

        stat_table_idx = None
        stat_rows: list[list[str]] = []
        age_tables: list[dict[str, object]] = []

        for i, el in enumerate(body):
            if el.name != "table":
                continue
            rows = table_to_rows(el)
            if not rows:
                continue
            if _is_stat_table(rows) and stat_table_idx is None:
                stat_table_idx = i
                stat_rows = rows
            elif _is_age_table(rows):
                age_tables.append(_parse_grid_table(rows))

        warnings: list[str] = []
        if stat_table_idx is None:
            paragraphs = [_norm(get_text(el)) for el in body if el.name == "p" and _norm(get_text(el))]
            joined = " ".join(paragraphs)
            if not paragraphs:
                continue

            rec: dict[str, object] = {
                "name": name,
                "description": "\n\n".join(paragraphs),
                "description_paragraphs": paragraphs,
                "stat_block": {},
                "dragon_age_tables": [],
                "warnings": ["missing_stat_block"],
            }

            see = re.search(r"\bSee\s+(.+?)(?:\.|$)", joined, re.IGNORECASE)
            if see:
                rec["cross_reference"] = _norm(see.group(1))
                rec["warnings"].append("cross_reference_only")

            monsters.append(rec)
            continue

        stat_block = _parse_stat_rows(stat_rows)
        missing_core = sorted(field for field in CORE_FIELDS if not stat_block.get(field))
        if missing_core:
            warnings.append("missing_core_fields:" + ",".join(missing_core))

        # Capture prose after the first stat table and before the next section.
        desc_paragraphs = []
        for el in body[stat_table_idx + 1 :]:
            if el.name == "p":
                t = _norm(get_text(el))
                if t:
                    desc_paragraphs.append(t)

        monster = {
            "name": name,
            "stat_block": stat_block,
            "description": "\n\n".join(desc_paragraphs),
            "description_paragraphs": desc_paragraphs,
            "dragon_age_tables": age_tables,
            "warnings": warnings,
        }
        monsters.append(monster)

    return monsters


def parse_phase4_data() -> list[dict[str, object]]:
    soup = load_html()
    elements = list(iter_elements(soup))
    return parse_monsters(elements)


def write_phase4_output(output_dir: str = "data") -> dict[str, int]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    monsters = parse_phase4_data()
    path = out_dir / OUTPUT_FILE
    with path.open("w", encoding="utf-8") as f:
        json.dump(monsters, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with_stats = sum(1 for m in monsters if m.get("stat_block"))
    with_warnings = sum(1 for m in monsters if m.get("warnings"))
    return {
        "monsters": len(monsters),
        "with_stat_block": with_stats,
        "with_warnings": with_warnings,
    }


if __name__ == "__main__":
    summary = write_phase4_output()
    for k, v in summary.items():
        print(f"{k}: {v}")
