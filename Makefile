PYTHON ?= .venv/bin/python

MANUAL_HTML := manual/Basic-Fantasy-RPG-Rules-r142.html

.PHONY: build test

build:
	@test -f "$(MANUAL_HTML)" || (echo "Missing $(MANUAL_HTML). Export the .odt manual to HTML and place it in manual/." && exit 1)
	$(PYTHON) src/generate_rules_tables.py
	$(PYTHON) src/generate_spells.py
	$(PYTHON) src/generate_monsters.py
	$(PYTHON) src/generate_treasure.py
	$(PYTHON) src/generate_characters_and_encounters.py
	$(PYTHON) src/generate_data_validation.py

test:
	$(PYTHON) tests/test_extraction_foundation.py
	$(PYTHON) tests/test_rules_tables.py
	$(PYTHON) tests/test_output_cleanup.py
	$(PYTHON) tests/test_spells.py
	$(PYTHON) tests/test_monsters.py
	$(PYTHON) tests/test_treasure.py
	$(PYTHON) tests/test_characters_and_encounters.py
	$(PYTHON) tests/test_data_validation.py
