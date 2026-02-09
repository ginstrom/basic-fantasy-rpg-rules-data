# Data Outputs

Generated structured JSON outputs from the Basic Fantasy RPG manual.

## Files

- `armor.json`: Armor and shield equipment table.
- `attack_bonus.json`: Attack bonus progression table.
- `class_tables.json`: Class progression tables (cleric/fighter/magic-user).
- `classes.json`: Class prose descriptions and labeled fields.
- `combat_tables.json`: Normalized combat-reference tables with source metadata.
- `encounter_tables.json`: Dungeon and wilderness encounter tables.
- `equipment.json`: General equipment tables.
- `magic_items.json`: Magic item entries parsed from prose sections.
- `magic_item_tables.json`: Random generation and magic-item roll tables.
- `monsters.json`: Monster records with stat blocks, descriptions, and warnings.
- `races.json`: Race prose descriptions and labeled fields.
- `saving_throws.json`: Saving throw progression by class.
- `spell_lists.json`: Spell indexes by class and level.
- `spells.json`: Individual spell records with metadata and descriptions.
- `thief_abilities.json`: Thief ability progression table.
- `treasure_types.json`: Treasure type and value tables.
- `turning_undead.json`: Cleric turning-undead progression table.
- `vehicles.json`: Land and water vehicle tables.
- `weapons.json`: Weapon table with per-item `category` values.
- `validation_report.json`: Cross-file validation report and unresolved warnings.

## Notes

- String normalization collapses OCR/layout whitespace artifacts.
- Numeric cleanup converts comma-formatted numbers (e.g. `1,000`) to integers.
- Numeric ranges (e.g. `1-3`) are normalized to integer lists.
- Some files include `warnings` arrays to preserve partial/edge parses.
- Encounter-to-monster references are validated heuristically.
