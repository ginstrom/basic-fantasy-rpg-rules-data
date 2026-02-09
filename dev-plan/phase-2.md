# Phase 2: Tables and Structured Data

## Objective

Extract core tabular rule data into normalized JSON files.

## Tasks

- [ ] Parse equipment tables (weapons, armor, gear, vehicles).
- [ ] Parse class level progression tables.
- [ ] Parse saving throw tables.
- [ ] Parse thief abilities table.
- [ ] Parse attack bonus table.
- [ ] Parse turning undead table.

## Technical Notes

- Prefer `pdfplumber` table extraction for grid-like content.
- Fall back to layout-text regex parsing when table detection fails.
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

- All planned table JSON files are generated.
- Files are valid JSON and contain non-empty records.
