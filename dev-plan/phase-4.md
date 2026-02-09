# Phase 4: Monsters

## Objective

Parse monster data into structured stat blocks with descriptions and special-case handling.

## Tasks

- [x] Parse standard single-entry stat blocks.
- [x] Handle multi-column variant monsters.
- [x] Handle dragon age tables.
- [x] Handle cross-reference-only entries.
- [x] Capture description text.

## Technical Notes

- Detect stat blocks from labeled lines (`Armor Class:`, `Hit Dice:`, etc.).
- Parse by field label rather than strict field order.
- Support variant layouts where multiple values appear on one labeled row.
- Record parse warnings for incomplete blocks rather than discarding records.

## Deliverables

- `data/monsters.json`

## Exit Criteria

- [x] Monster count is within expected range (~200+).
- [x] Core stat fields are present for most entries.
- [x] Exceptions are recorded with parse warnings.
