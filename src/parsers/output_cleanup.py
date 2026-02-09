"""Post-generation cleanup/normalization for extracted JSON outputs."""

from __future__ import annotations

import re
from typing import Any


_COMMA_INT_RE = re.compile(r"^[0-9]{1,3}(?:,[0-9]{3})+$")
_INT_RANGE_RE = re.compile(r"^([0-9]+)-([0-9]+)$")


def _parse_int_with_commas(value: str) -> int | None:
    if not _COMMA_INT_RE.fullmatch(value):
        return None
    return int(value.replace(",", ""))


def _parse_numeric_range(value: str) -> list[int] | None:
    """Convert integer range strings to inclusive integer lists.

    Examples:
    - "1-3" -> [1, 2, 3]
    - "01-25" -> [1, ..., 25]
    - "98-00" -> [98, 99, 100]  (percentile wrap where 00 == 100)
    """

    m = _INT_RANGE_RE.fullmatch(value)
    if not m:
        return None

    start = int(m.group(1))
    end = int(m.group(2))

    # Percentile table convention uses 00 for 100.
    if end == 0:
        end = 100

    if start <= end:
        return list(range(start, end + 1))

    # Preserve unknown descending ranges without transformation.
    return None


def _normalize_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    comma_int = _parse_int_with_commas(value)
    if comma_int is not None:
        return comma_int

    numeric_range = _parse_numeric_range(value)
    if numeric_range is not None:
        return numeric_range

    return value


def _normalize_ranges_and_numbers(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize_ranges_and_numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalize_ranges_and_numbers(v) for v in value]
    return _normalize_scalar(value)


def normalize_weapon_categories(weapons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fold header rows into per-item category attributes.

    Input has rows like {"weapon":"Axes", "price":"", "size":"", "weight":"", "dmg":""}.
    Output removes those pseudo-items and annotates following rows with:
      {"category":"Axes", ...}
    """

    out: list[dict[str, Any]] = []
    current_category: str | None = None

    for row in weapons:
        weapon = str(row.get("weapon", "")).strip()
        is_header = (
            bool(weapon)
            and str(row.get("price", "")).strip() == ""
            and str(row.get("size", "")).strip() == ""
            and str(row.get("weight", "")).strip() == ""
            and str(row.get("dmg", "")).strip() == ""
        )
        if is_header:
            current_category = weapon
            continue

        normalized = dict(row)
        if current_category and "category" not in normalized:
            normalized["category"] = current_category
        out.append(normalized)

    return out


def cleanup_payload(name: str, payload: Any) -> Any:
    cleaned = _normalize_ranges_and_numbers(payload)
    if name == "weapons" and isinstance(cleaned, list):
        cleaned = normalize_weapon_categories(cleaned)
    return cleaned
