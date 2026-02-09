# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Parse the Basic Fantasy RPG 4th Edition (Release 142) manual into structured JSON data files. The source is an HTML export at `manual/Basic-Fantasy-RPG-Rules-r142.html` (LibreOffice HTML, CC BY-SA 4.0).

## Development Practices

- Treat each phase as a full git workflow:
  - Start by creating a feature branch from `main` (for example: `phase-2-tables`).
  - Implement and validate the phase scope on that branch.
  - Finish by committing all phase changes and merging the branch back to `main`.
- Keep commits small and logically consistent:
  - One logical change per commit (avoid mixing refactors, behavior changes, and docs in the same commit unless tightly coupled).
  - Commit frequently at stable checkpoints rather than one large end-of-phase commit.
  - Each commit must leave the branch in a runnable, testable state.
- Use clear commit messages that describe intent and impact.
- Run relevant tests/validation before each commit and again before merging.
- Update documentation (`README.md`, parser notes, and schema docs) when behavior, CLI, or data formats change.
- Keep `main` stable; do phase work on feature branches and merge only validated changes.
- Never commit generated artifacts unless explicitly required; generated parser output belongs in `data/` and can be regenerated.

## Python Environment

- Use a local virtual environment for all Python commands.
- Create and activate it before installing or running tooling:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Run Python tooling via the virtualenv interpreter (for example: `.venv/bin/python -m ...`).

## Key Context

- The primary source is the HTML manual at `manual/Basic-Fantasy-RPG-Rules-r142.html` (LibreOffice HTML export). It preserves semantic structure: headings use `SoutaneBlack` font, tables are real `<table>` elements, and content flows linearly.
- Multi-column page sections are wrapped in `<div>` elements with `column-count: 2` CSS. The extraction pipeline flattens these automatically.
- Pre-extracted text files from the PDF still exist in `manual/manual.txt` (flow mode) and `manual/manual-layout.txt` (layout mode) but are not used by the current pipeline.
- The development plan with full data schemas, parsing strategies, and architecture is in `dev-plan/plan.md`.

## HTML Document Structure

- **Section headers**: `<p>` elements containing `<font face="SoutaneBlack">` — detected by `is_section_header()`.
- **PART headers**: Section headers whose text starts with "PART N:" — detected by `is_part_header()`.
- **Tables**: Standard `<table>` elements with `<th>` headers and `<td>` cells. Parsed via `table_to_rows()`.
- **Spell entries**: `<p>` with bold name + "Range:" on the same line, followed by class/level + duration, then description paragraphs.
- **Monster stat blocks**: SoutaneBlack name header, followed by `<table>` with rows for Armor Class, Hit Dice, No. of Attacks, Damage, Movement, No. Appearing, Save As, Morale, Treasure Type, XP.

## Manual Structure (page ranges from TOC)

| Section | Pages | Key Data |
|---------|-------|----------|
| Part 2: Player Characters | 3-14 | Races, classes, level tables, equipment, weapons, armor |
| Part 3: Spells | 15-41 | ~97 spells (Cleric + Magic-User) |
| Part 5: The Encounter | 50-61 | Attack bonus table, saving throws, turning undead |
| Part 6: Monsters | 62-162 | ~200 monsters with stat blocks |
| Part 7: Treasure | 163-179 | Treasure types, magic items |
| Part 8: GM Information | 180-202 | Wandering monster/encounter tables |

## Extraction Metrics (Release 142 HTML)

| Metric                     | Observed |
|----------------------------|----------|
| Top-level elements         | 3241     |
| Section headers            | 396      |
| Tables                     | 296      |
| Weapons table rows         | 40       |
| Spell entries (alpha list) | 97       |
| Monster stat block tables  | 200      |

## Commands

```bash
# Install dependencies
.venv/bin/pip install -r requirements.txt

# Run phase 1 extraction validation
.venv/bin/python tests/test_phase1_extraction.py
```

## Architecture

Parser code goes in `src/`, output JSON goes in `data/`. See `dev-plan/plan.md` for full schema definitions and the section-by-section parsing strategy.

### Current files

- `src/extract_text.py` — HTML loading and text extraction (BeautifulSoup/lxml)
- `src/column_splitter.py` — Section navigation utilities (find_section, elements_between, etc.)
- `src/parsers/` — Section-specific parsers (spells, monsters, equipment, treasure, etc.)
- `tests/test_phase1_extraction.py` — Extraction quality validation

### Key API patterns

```python
from extract_text import load_html, iter_elements, table_to_rows, is_section_header
from column_splitter import find_section, elements_between, elements_between_parts, collect_sections

soup = load_html()
elements = list(iter_elements(soup))          # Flattened document elements
idx = find_section(elements, "Weapons")       # Find section by header text
elems = elements_between(elements, "Start")   # Elements from header to next header
elems = elements_between_parts(elements, 6, 7)  # Elements between PART headers
rows = table_to_rows(table_tag)               # Table → list[list[str]]
sections = collect_sections(elements)         # Dict mapping header text → child elements
```

## Repository Conventions

- Keep implementation code under `src/`.
- Keep parser outputs and generated JSON under `data/`.
- Keep source/reference assets (such as the manual HTML and images) under `manual/`.
- Keep plans and design docs under `dev-plan/`.

## Progress

- **Phase 1**: Foundation — HTML extraction pipeline complete. 14/14 tests passing.
- **Phase 1.1**: Validation tightening — Baselines documented, thresholds tightened.
- **Phase 2–7**: Pending. See `dev-plan/` for details.

## License

CC BY-SA 4.0. All data derived from Chris Gonnerman's Basic Fantasy RPG. Artwork from the original manual is NOT covered by this license and must not be redistributed.
