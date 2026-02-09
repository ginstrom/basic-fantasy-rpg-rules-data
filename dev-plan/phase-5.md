# Phase 5: Treasure and Magic Items

## Objective

Extract treasure tables, random generation tables, and magic item descriptions.

## Tasks

- [ ] Parse treasure type tables (A-T).
- [ ] Parse random generation tables (`d%` tables).
- [ ] Parse magic item descriptions by category.

## Technical Notes

- Use table extraction first for treasure grid pages.
- Use regex patterns for roll-range tables (e.g., `01-15 Item Name`).
- Split prose item entries by item-name boundaries and retain full descriptions.

## Deliverables

- `data/treasure_types.json`
- `data/magic_items.json`
- `data/magic_item_tables.json`

## Exit Criteria

- All three output files are generated and non-empty.
- Table rows and item entries parse without critical structural errors.
