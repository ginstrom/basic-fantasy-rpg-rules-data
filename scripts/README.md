# Scripts

This directory is for runnable scripts that generate/update JSON outputs from the HTML manual.

Current extraction entrypoints live in `src/` as:
- `src/generate_rules_tables.py`
- `src/generate_spells.py`
- `src/generate_monsters.py`
- `src/generate_treasure.py`
- `src/generate_characters_and_encounters.py`
- `src/generate_data_validation.py`

Run them with the project virtualenv, for example:

```bash
.venv/bin/python src/generate_monsters.py
```
