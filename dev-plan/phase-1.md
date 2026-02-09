# Phase 1: Foundation

## Objective

Establish a reliable HTML extraction pipeline that preserves document order,
section boundaries, and table structure for downstream parsers.

## Tasks

- [x] Set up Python project dependencies (`beautifulsoup4`, `lxml`) and environment.
- [x] Implement HTML loading and normalized text extraction utilities.
- [x] Implement section navigation helpers for header/part-based traversal.
- [x] Test extraction quality on representative sections and content domains.

## Technical Notes

- Use BeautifulSoup + lxml to parse `manual/Basic-Fantasy-RPG-Rules-r142.html`.
- Treat `<p>` with `SoutaneBlack` font as section headers.
- Flatten `<div>` column wrappers while preserving document order for `<p>` and `<table>`.
- Prefer semantic extraction from HTML elements instead of coordinate/layout heuristics.

## Deliverables

- `src/extract_text.py` for HTML parsing and table/text helpers.
- `src/column_splitter.py` for section/part navigation utilities.
- `tests/test_phase1_extraction.py` for extraction quality checks.

## Exit Criteria

- Section and table traversal supports all downstream planned domains.
- Representative extraction checks pass for sections, tables, spells, and monsters.

## Execution Review (2026-02-09)

Reported completion was reviewed by running:

```bash
.venv/bin/python tests/test_phase1_extraction.py
```

Result: `14/14` checks passed.

Observed extraction metrics from the run:

- Top-level content elements: `3241`
- Section headers detected: `396`
- Tables detected: `296`
- Weapons table parsed with expected headers and `40` rows
- Monster stat block tables detected in PART 6: `200`

Review outcome: Phase 1 completion claim is supported by the current test suite and implementation.

Follow-up note:

- The spell-count expectation comment in the test (`~65-70`) is stale versus current observed count (`97`) and should be tightened in a later validation pass.
