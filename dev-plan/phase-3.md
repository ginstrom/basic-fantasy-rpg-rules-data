# Phase 3: Spells

## Objective

Parse spell lists and full spell descriptions with class/level metadata and special cases.

## Tasks

- [ ] Parse spell index by class and level.
- [ ] Parse all individual spell entries.
- [ ] Handle reversible spells.
- [ ] Extract embedded spell tables where present.

## Technical Notes

- Spell pages require robust column splitting before entry parsing.
- Detect spell boundaries from header + `Range:` and `Duration:` patterns.
- Parse class/level lines such as `Cleric 4, Magic-User 5`.
- Preserve parse warnings instead of dropping partial entries.

## Deliverables

- `data/spells.json`
- `data/spell_lists.json`

## Exit Criteria

- Parsed spell count is within expected range (~65-70).
- All entries include class/level metadata.
