# Phase 2: Tables and Structured Data

## Objective

Extract core tabular rule data into normalized JSON files.

## Tasks

- [x] Parse equipment tables (weapons, armor, gear, vehicles).
- [x] Parse class level progression tables.
- [x] Parse saving throw tables.
- [x] Parse thief abilities table.
- [x] Parse attack bonus table.
- [x] Parse turning undead table.

## Technical Notes

- Prefer semantic HTML `<table>` parsing via `table_to_rows` for grid-like content.
- Fall back to section-scoped text pattern parsing when table markup is irregular.
- Normalize row/column naming across outputs for consistent downstream use.

## Deliverables

- `data/weapons.json`
- `data/armor.json`
- `data/equipment.json`
- `data/vehicles.json`
- `data/class_tables.json`
- `data/saving_throws.json`
- `data/thief_abilities.json`
- `data/attack_bonus.json`
- `data/turning_undead.json`

## Exit Criteria

- [x] All planned table JSON files are generated.
- [x] Files are valid JSON and contain non-empty records.
