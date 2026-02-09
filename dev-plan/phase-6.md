# Phase 6: Races, Classes, and Encounters

## Objective

Complete remaining core content domains: races, classes, encounter tables, and combat references.

## Tasks

- [x] Parse race data.
- [x] Parse class descriptions.
- [x] Parse dungeon encounter tables.
- [x] Parse wilderness encounter tables.
- [x] Parse combat reference tables.

## Technical Notes

- Use known section/page bounds to avoid cross-section contamination.
- Normalize encounter table shapes for consistent consumer logic.
- Store combat tables in a common schema with table-name and source metadata.

## Deliverables

- `data/races.json`
- `data/classes.json`
- `data/encounter_tables.json`
- `data/combat_tables.json`

## Exit Criteria

- [x] All outputs are generated with expected top-level keys and row counts.
- [x] Encounter and combat table structures are consistent and machine-readable.
