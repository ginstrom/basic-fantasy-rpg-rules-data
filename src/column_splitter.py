"""Section navigation utilities for the Basic Fantasy RPG HTML manual.

Replaces the PDF column-splitter — with HTML we instead need tools to
locate and iterate over named sections of the document.
"""

from __future__ import annotations

from bs4 import Tag

from extract_text import (
    get_section_header_text,
    get_text,
    is_part_header,
    is_section_header,
    iter_elements,
)


def find_section(elements: list[Tag], header_text: str) -> int | None:
    """Return the index of the element whose SoutaneBlack header matches *header_text*.

    Matching is case-insensitive and ignores leading/trailing whitespace.
    """
    target = header_text.strip().lower()
    for i, el in enumerate(elements):
        if is_section_header(el):
            text = get_section_header_text(el)
            if text and text.strip().lower() == target:
                return i
    return None


def find_part(elements: list[Tag], part_number: int) -> int | None:
    """Return the index of the PART header with the given number.

    Skips TOC entries (which have trailing page numbers) and returns
    the actual section header.
    """
    import re

    target = f"PART {part_number}:"
    for i, el in enumerate(elements):
        if is_part_header(el) and is_section_header(el):
            text = get_text(el)
            if text.upper().startswith(target.upper()):
                return i
    # Fallback: match any PART header without a trailing page number
    for i, el in enumerate(elements):
        if is_part_header(el):
            text = get_text(el)
            if text.upper().startswith(target.upper()) and not re.search(r"\d+$", text.strip()):
                return i
    return None


def elements_between(
    elements: list[Tag],
    start_header: str,
    stop_header: str | None = None,
) -> list[Tag]:
    """Return elements between *start_header* and *stop_header* (exclusive).

    If *stop_header* is None, returns everything from *start_header* to the
    next SoutaneBlack header at the same level.
    """
    start = find_section(elements, start_header)
    if start is None:
        return []

    result = []
    for el in elements[start + 1 :]:
        if stop_header and is_section_header(el):
            text = get_section_header_text(el)
            if text and text.strip().lower() == stop_header.strip().lower():
                break
        elif stop_header is None and is_section_header(el):
            break
        result.append(el)
    return result


def elements_between_parts(
    elements: list[Tag], start_part: int, end_part: int | None = None
) -> list[Tag]:
    """Return all elements between two PART headers."""
    start = find_part(elements, start_part)
    if start is None:
        return []

    result = []
    for el in elements[start + 1 :]:
        if end_part is not None and is_part_header(el):
            text = get_text(el)
            if text.upper().startswith(f"PART {end_part}:"):
                break
        result.append(el)
    return result


def collect_sections(elements: list[Tag]) -> dict[str, list[Tag]]:
    """Build a dict mapping each SoutaneBlack header to its child elements."""
    sections: dict[str, list[Tag]] = {}
    current_key: str | None = None
    current_elems: list[Tag] = []

    for el in elements:
        if is_section_header(el):
            if current_key is not None:
                sections[current_key] = current_elems
            current_key = get_section_header_text(el) or ""
            current_elems = []
        elif current_key is not None:
            current_elems.append(el)

    if current_key is not None:
        sections[current_key] = current_elems

    return sections
