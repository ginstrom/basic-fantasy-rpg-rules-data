# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Parse the Basic Fantasy RPG 4th Edition (Release 142) PDF manual into structured JSON data files. The source PDF is at `manual/Basic-Fantasy-RPG-Rules-r142.pdf` (208 pages, two-column layout, CC BY-SA 4.0).

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

# Run the parser (planned, not yet implemented)
pip install pdfplumber
python scripts/parse_manual.py manual/Basic-Fantasy-RPG-Rules-r142.pdf --output data/
python scripts/validate.py data/
```

## Planned Architecture

Parser scripts go in `scripts/`, output JSON goes in `data/`. See `dev-plan/plan.md` for full schema definitions and the section-by-section parsing strategy. Key files:

- `scripts/parse_manual.py` — CLI entry point
- `scripts/extract_text.py` — PDF text extraction via pdfplumber
- `scripts/column_splitter.py` — two-column layout separation
- `scripts/parsers/` — section-specific parsers (spells, monsters, equipment, treasure, etc.)
- `scripts/validate.py` — cross-reference validation

## License

CC BY-SA 4.0. All data derived from Chris Gonnerman's Basic Fantasy RPG. Artwork from the original manual is NOT covered by this license and must not be redistributed.
