"""Phase 3 parser: spell lists and spell entries."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import Tag

from column_splitter import elements_between
from extract_text import get_text, get_text_preserve_whitespace, iter_elements, load_html, table_to_rows

OUTPUT_FILES = {
    "spells": "spells.json",
    "spell_lists": "spell_lists.json",
}


_CLASS_RE = re.compile(r"(Cleric|Magic-User)\s*(\d+)", re.IGNORECASE)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _parse_level_word(text: str) -> int | None:
    words = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
    }
    s = _norm(text).lower()
    for word, num in words.items():
        if s.startswith(word + " "):
            return num
    m = re.match(r"(\d+)", s)
    return int(m.group(1)) if m else None


def _parse_spell_list_section(elements: list[Tag], header: str, class_key: str) -> dict[int, list[str]]:
    section = elements_between(elements, header)
    out: dict[int, list[str]] = {}
    current_level: int | None = None

    for el in section:
        if el.name == "p":
            t = get_text(el)
            if "Level" in t and "Spells" in t:
                current_level = _parse_level_word(t)
        elif el.name == "table" and current_level is not None:
            rows = table_to_rows(el)
            names = []
            for row in rows:
                if len(row) < 2:
                    continue
                name = _norm(row[1])
                if not name:
                    continue
                names.append(name)
            out[current_level] = names
            current_level = None

    return out


def parse_spell_lists(elements: list[Tag]) -> dict[str, object]:
    cleric = _parse_spell_list_section(elements, "Cleric Spells", "cleric")
    magic_user = _parse_spell_list_section(elements, "Magic-User Spells", "magic_user")

    all_rows = []
    for class_key, levels in [("cleric", cleric), ("magic_user", magic_user)]:
        for level in sorted(levels):
            for name in levels[level]:
                all_rows.append(
                    {
                        "class": class_key,
                        "level": level,
                        "name": name,
                        "reversible": name.endswith("*"),
                        "name_clean": name.rstrip("*"),
                    }
                )

    return {
        "cleric": {str(k): v for k, v in sorted(cleric.items())},
        "magic_user": {str(k): v for k, v in sorted(magic_user.items())},
        "all": all_rows,
    }


def _extract_spell_range(header_text: str) -> str:
    if "Range:" not in header_text:
        return ""
    return _norm(header_text.split("Range:", 1)[1])


def _extract_meta(meta_text: str) -> tuple[dict[str, int], str]:
    class_levels: dict[str, int] = {}

    if "Duration:" in meta_text:
        class_part, duration_part = meta_text.split("Duration:", 1)
        duration = _norm(duration_part)
    else:
        class_part = meta_text
        duration = ""

    for cls, lvl in _CLASS_RE.findall(class_part):
        class_levels[_slug(cls)] = int(lvl)

    return class_levels, duration


def parse_spells(elements: list[Tag]) -> list[dict[str, object]]:
    section = elements_between(elements, "All Spells, in Alphabetical Order")

    starts: list[int] = []
    for i, el in enumerate(section):
        if el.name != "p":
            continue
        text = get_text_preserve_whitespace(el)
        if "Range:" in text and el.find("b") is not None:
            starts.append(i)

    out: list[dict[str, object]] = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(section)

        head = section[start]
        head_text = _norm(get_text_preserve_whitespace(head))
        b = head.find("b")
        if b is None:
            continue

        name = _norm(b.get_text(" ", strip=True))
        name_clean = name.rstrip("*")
        reversible = name.endswith("*")

        warnings: list[str] = []
        spell_range = _extract_spell_range(head_text)
        if not spell_range:
            warnings.append("missing_range")

        meta_idx = None
        class_levels: dict[str, int] = {}
        duration = ""
        for j in range(start + 1, min(end, start + 5)):
            el = section[j]
            if el.name != "p":
                continue
            t = _norm(get_text_preserve_whitespace(el))
            if "Duration:" in t:
                class_levels, duration = _extract_meta(t)
                meta_idx = j
                break

        if meta_idx is None:
            warnings.append("missing_class_duration_line")
        if not class_levels:
            warnings.append("missing_class_levels")
        if not duration:
            warnings.append("missing_duration")

        desc_start = (meta_idx + 1) if meta_idx is not None else (start + 1)
        paragraphs: list[str] = []
        embedded_tables: list[dict[str, object]] = []

        for j in range(desc_start, end):
            el = section[j]
            if el.name == "p":
                txt = _norm(get_text_preserve_whitespace(el))
                if txt:
                    paragraphs.append(txt)
            elif el.name == "table":
                rows = table_to_rows(el)
                if rows:
                    headers = rows[0]
                    table_rows = [r for r in rows[1:] if any(c.strip() for c in r)]
                    embedded_tables.append({
                        "headers": headers,
                        "rows": table_rows,
                    })

        out.append(
            {
                "name": name,
                "name_clean": name_clean,
                "reversible": reversible,
                "range": spell_range,
                "duration": duration,
                "class_levels": class_levels,
                "description_paragraphs": paragraphs,
                "description": "\n\n".join(paragraphs),
                "embedded_tables": embedded_tables,
                "warnings": warnings,
            }
        )

    return out


def parse_phase3_data() -> dict[str, object]:
    soup = load_html()
    elements = list(iter_elements(soup))

    return {
        "spells": parse_spells(elements),
        "spell_lists": parse_spell_lists(elements),
    }


def write_phase3_outputs(output_dir: str = "data") -> dict[str, int]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_phase3_data()
    counts: dict[str, int] = {}

    for key, filename in OUTPUT_FILES.items():
        path = out_dir / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(parsed[key], f, indent=2, ensure_ascii=False)
            f.write("\n")

        if key == "spells":
            counts[key] = len(parsed[key])
        elif key == "spell_lists":
            counts[key] = len(parsed[key].get("all", []))
        else:
            counts[key] = 0

    return counts


if __name__ == "__main__":
    summary = write_phase3_outputs()
    for name in OUTPUT_FILES:
        print(f"{name}: {summary.get(name, 0)}")
