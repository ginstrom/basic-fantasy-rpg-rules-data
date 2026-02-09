# Data Outputs

Generated structured JSON outputs from the Basic Fantasy RPG manual.

## Files

- [`armor.json`](./armor.json): Armor and shield equipment table.
- [`attack_bonus.json`](./attack_bonus.json): Attack bonus progression table.
- [`class_tables.json`](./class_tables.json): Class progression tables (cleric/fighter/magic-user).
- [`classes.json`](./classes.json): Class prose descriptions and labeled fields.
- [`combat_tables.json`](./combat_tables.json): Normalized combat-reference tables with source metadata.
- [`encounter_tables.json`](./encounter_tables.json): Dungeon and wilderness encounter tables.
- [`equipment.json`](./equipment.json): General equipment tables.
- [`magic_items.json`](./magic_items.json): Magic item entries parsed from prose sections.
- [`magic_item_tables.json`](./magic_item_tables.json): Random generation and magic-item roll tables.
- [`monsters.json`](./monsters.json): Monster records with stat blocks, descriptions, and warnings.
- [`races.json`](./races.json): Race prose descriptions and labeled fields.
- [`saving_throws.json`](./saving_throws.json): Saving throw progression by class.
- [`spell_lists.json`](./spell_lists.json): Spell indexes by class and level.
- [`spells.json`](./spells.json): Individual spell records with metadata and descriptions.
- [`thief_abilities.json`](./thief_abilities.json): Thief ability progression table.
- [`treasure_types.json`](./treasure_types.json): Treasure type and value tables.
- [`turning_undead.json`](./turning_undead.json): Cleric turning-undead progression table.
- [`validation_report.json`](./validation_report.json): Cross-file validation report and unresolved warnings.
- [`vehicles.json`](./vehicles.json): Land and water vehicle tables.
- [`weapons.json`](./weapons.json): Weapon table.

## Notes

- String normalization collapses OCR/layout whitespace artifacts.
- Some files include `warnings` arrays to preserve partial/edge parses.
- Encounter-to-monster references are validated heuristically.
