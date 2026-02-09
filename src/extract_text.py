"""HTML-based text extraction for the Basic Fantasy RPG manual.

The manual is available as a LibreOffice HTML export which preserves
semantic structure: headings use SoutaneBlack font, tables are real
<table> elements, and content flows linearly (no column-splitting
needed).

The HTML wraps multi-column page sections inside <div> elements with
``column-count: 2``.  :func:`iter_elements` flattens these so that
all ``<p>`` and ``<table>`` elements appear in document order.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag

HTML_PATH = "manual/Basic-Fantasy-RPG-Rules-r142.html"


def load_html(path: str = HTML_PATH) -> BeautifulSoup:
    """Parse the manual HTML and return a BeautifulSoup tree."""
    with open(path, encoding="utf-8") as f:
        return BeautifulSoup(f, "lxml")


def _normalize(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    return re.sub(r"\s+", " ", text).strip()


def is_section_header(tag: Tag) -> bool:
    """Return True if a tag is a section header (SoutaneBlack font)."""
    if tag.name != "p":
        return False
    font = tag.find("font", attrs={"face": "SoutaneBlack"})
    return font is not None


def get_section_header_text(tag: Tag) -> str | None:
    """Extract normalized header text from a SoutaneBlack-font paragraph."""
    font = tag.find("font", attrs={"face": "SoutaneBlack"})
    if font:
        return _normalize(font.get_text())
    return None


def is_part_header(tag: Tag) -> bool:
    """Return True if a tag is a PART-level header (14pt font)."""
    if tag.name != "p":
        return False
    text = _normalize(tag.get_text())
    return text.upper().startswith("PART")


def get_text(tag: Tag) -> str:
    """Get cleaned, whitespace-normalized text content from a tag."""
    return _normalize(tag.get_text())


def get_text_preserve_whitespace(tag: Tag) -> str:
    """Get text content preserving internal whitespace (tabs, etc.)."""
    return tag.get_text().strip()


def table_to_rows(table: Tag) -> list[list[str]]:
    """Convert an HTML <table> into a list of rows, each a list of cell texts.

    Nested tables are ignored — only direct ``<tr>`` children of the
    outermost ``<table>`` (or its ``<thead>``/``<tbody>``) are included.
    """
    rows = []
    for tr in table.find_all("tr", recursive=True):
        # Skip rows that belong to a nested table
        if tr.find_parent("table") is not table:
            continue
        cells = []
        for cell in tr.find_all(["td", "th"], recursive=False):
            cells.append(_normalize(cell.get_text()))
        if cells:
            rows.append(cells)
    return rows


def find_all_tables(soup: BeautifulSoup) -> list[Tag]:
    """Return all <table> elements in the document."""
    return soup.find_all("table")


def iter_elements(soup: BeautifulSoup):
    """Iterate over content elements in document order.

    Flattens ``<div>`` wrappers (used for two-column CSS layouts) so
    that their child ``<p>``, ``<table>``, and ``<h3>`` elements appear
    directly in the stream alongside top-level elements.
    """
    body = soup.find("body")
    if body is None:
        return
    for child in body.children:
        if not isinstance(child, Tag):
            continue
        if child.name == "div":
            # Flatten: yield the div's children instead
            for subchild in child.children:
                if isinstance(subchild, Tag):
                    yield subchild
        else:
            yield child
