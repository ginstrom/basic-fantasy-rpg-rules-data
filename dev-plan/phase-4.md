# Phase 4: Monsters

## Objective

Parse monster data into structured stat blocks with descriptions and special-case handling.

## Tasks

- [ ] Parse standard single-entry stat blocks.
- [ ] Handle multi-column variant monsters.
- [ ] Handle dragon age tables.
- [ ] Handle cross-reference-only entries.
- [ ] Capture description text.

## Technical Notes

- Detect stat blocks from labeled lines (`Armor Class:`, `Hit Dice:`, etc.).
- Parse by field label rather than strict field order.
- Support variant layouts where multiple values appear on one labeled row.
- Record parse warnings for incomplete blocks rather than discarding records.

## Deliverables

- `data/monsters.json`

## Exit Criteria

- Monster count is within expected range (~200+).
- Core stat fields are present for most entries.
- Exceptions are recorded with parse warnings.
