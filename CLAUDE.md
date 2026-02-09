# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Parse the Basic Fantasy RPG 4th Edition (Release 142) PDF manual into structured JSON data files. The source PDF is at `manual/Basic-Fantasy-RPG-Rules-r142.pdf` (208 pages, two-column layout, CC BY-SA 4.0).

## Development Practices

- Use small, focused changes and keep commits atomic (one logical change per commit).
- Use clear commit messages that describe intent and impact.
- Run relevant tests/validation before committing and again before pushing.
- Update documentation (`README.md`, parser notes, and schema docs) when behavior, CLI, or data formats change.
- Prefer feature branches and pull requests for non-trivial work; keep `main` stable.
- Never commit generated artifacts unless explicitly required; generated parser output belongs in `data/` and can be regenerated.

## Python Environment

- Use a local virtual environment for all Python commands.
- Create and activate it before installing or running tooling:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

- Run Python tooling via the virtualenv interpreter (for example: `.venv/bin/python -m ...`).

## Key Context

- The PDF is too large (~106MB) for direct `Read` tool access. Use `pdftotext` (poppler-utils, already installed) or Python `pdfplumber` for text extraction.
- Pre-extracted text files exist in `manual/manual.txt` (flow mode, ~25k lines) and `manual/manual-layout.txt` (layout mode, ~11.7k lines). Layout mode preserves the two-column spatial arrangement.
- The development plan with full data schemas, parsing strategies, and architecture is in `dev-plan/plan.md`.

## PDF Structure (page ranges from TOC)

| Section | Pages | Key Data |
|---------|-------|----------|
| Part 2: Player Characters | 3-14 | Races, classes, level tables, equipment, weapons, armor |
| Part 3: Spells | 15-41 | ~65-70 spells (Cleric + Magic-User) |
| Part 5: The Encounter | 50-61 | Attack bonus table, saving throws, turning undead |
| Part 6: Monsters | 62-162 | ~200+ monsters with stat blocks |
| Part 7: Treasure | 163-179 | Treasure types, magic items |
| Part 8: GM Information | 180-202 | Wandering monster/encounter tables |

## Critical Parsing Challenges

- **Two-column layout**: The PDF places two entries side-by-side. `pdftotext -layout` preserves this as wide lines with both columns; `pdftotext` (flow mode) interleaves paragraphs from both columns unpredictably. Column gutter is roughly at character position 52-58 in layout mode.
- **Monster variants**: Some monsters have multi-column stat blocks (e.g., Ant Giant/Huge/Large) or complex age tables (dragons).
- **Page headers/footers**: Lines like `BASIC FANTASY RPG`, `MONSTERS`, `SPELLS`, and bare page numbers appear throughout extracted text and must be stripped.

## Commands

```bash
# Extract text from PDF (already done, but for re-extraction)
pdftotext manual/Basic-Fantasy-RPG-Rules-r142.pdf manual/manual.txt
pdftotext -layout manual/Basic-Fantasy-RPG-Rules-r142.pdf manual/manual-layout.txt

# Extract a single page range (layout mode)
pdftotext -f 15 -l 41 -layout manual/Basic-Fantasy-RPG-Rules-r142.pdf /dev/stdout

# Install dependencies and run parser/validation from virtualenv
.venv/bin/pip install pdfplumber
.venv/bin/python src/parse_manual.py manual/Basic-Fantasy-RPG-Rules-r142.pdf --output data/
.venv/bin/python src/validate.py data/
```

## Planned Architecture

Parser code goes in `src/`, output JSON goes in `data/`. See `dev-plan/plan.md` for full schema definitions and the section-by-section parsing strategy. Key files:

- `src/parse_manual.py` — CLI entry point
- `src/extract_text.py` — PDF text extraction via pdfplumber
- `src/column_splitter.py` — two-column layout separation
- `src/parsers/` — section-specific parsers (spells, monsters, equipment, treasure, etc.)
- `src/validate.py` — cross-reference validation

## Repository Conventions

- Keep implementation code under `src/`.
- Keep parser outputs and generated JSON under `data/`.
- Keep source/reference assets (such as the manual PDF and extracted raw text) under `manual/`.
- Keep plans and design docs under `dev-plan/`.

## License

CC BY-SA 4.0. All data derived from Chris Gonnerman's Basic Fantasy RPG. Artwork from the original manual is NOT covered by this license and must not be redistributed.
