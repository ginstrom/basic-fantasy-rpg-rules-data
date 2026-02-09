# Phase 3: Spells

## Objective

Parse spell lists and full spell descriptions with class/level metadata and special cases.

## Tasks

- [x] Parse spell index by class and level.
- [x] Parse all individual spell entries.
- [x] Handle reversible spells.
- [x] Extract embedded spell tables where present.

## Technical Notes

- Spell parsing should rely on HTML section boundaries rather than page-column heuristics.
- Detect spell boundaries from header + `Range:` and `Duration:` patterns.
- Parse class/level lines such as `Cleric 4, Magic-User 5`.
- Preserve parse warnings instead of dropping partial entries.

## Deliverables

- `data/spells.json`
- `data/spell_lists.json`

## Exit Criteria

- [x] Parsed spell count is within expected range (~97 for Release 142).
- [x] All entries include class/level metadata.
