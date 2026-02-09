"""Phase 1 extraction quality tests.

Validates that the HTML-based extraction correctly identifies sections,
parses tables, and preserves content structure.

Baseline metrics (Release 142 HTML export):
  - Top-level elements: 3241
  - Section headers (SoutaneBlack font): 396
  - Tables: 296
  - Weapons table rows: 40
  - Spell entries (alphabetical listing): 97
  - Monster stat block tables (PART 6): 200

To re-run:
    .venv/bin/python tests/test_phase1_extraction.py
"""

import sys
sys.path.insert(0, "src")

from extract_text import (
    load_html,
    get_section_header_text,
    table_to_rows,
    iter_elements,
    is_section_header,
)
from column_splitter import (
    collect_sections,
    find_section,
    elements_between,
    elements_between_parts,
)

# --- Validated baselines (Release 142 HTML) ---
EXPECTED_SECTIONS_MIN = 390
EXPECTED_TABLES_MIN = 290
EXPECTED_WEAPONS_ROWS_MIN = 35
EXPECTED_SPELLS_MIN = 90
EXPECTED_MONSTERS_MIN = 190


def main():
    print("Loading HTML manual...")
    soup = load_html()
    elements = list(iter_elements(soup))
    print(f"Total top-level elements: {len(elements)}")

    passed = 0
    failed = 0

    # --- Test 1: Section headers detected ---
    sections = collect_sections(elements)
    section_names = list(sections.keys())
    print(f"\nSections found: {len(section_names)}")
    for name in section_names[:20]:
        print(f"  {name}")
    if len(section_names) > 20:
        print(f"  ... and {len(section_names) - 20} more")

    if len(section_names) >= EXPECTED_SECTIONS_MIN:
        print(f"[PASS] Found {len(section_names)} section headers (expected >={EXPECTED_SECTIONS_MIN})")
        passed += 1
    else:
        print(f"[FAIL] Expected >={EXPECTED_SECTIONS_MIN} sections, got {len(section_names)}")
        failed += 1

    # --- Test 2: Key sections exist ---
    expected_sections = [
        "Dwarves", "Fighter", "Weapons",
        "Cleric Spells", "Magic-User Spells",
        "Saving Throws", "Monster Descriptions", "Treasure Types",
    ]
    for name in expected_sections:
        idx = find_section(elements, name)
        if idx is not None:
            print(f"[PASS] Section '{name}' found at index {idx}")
            passed += 1
        else:
            matches = [s for s in section_names if name.lower() in s.lower()]
            if matches:
                print(f"[PASS] Section '{name}' found as '{matches[0]}'")
                passed += 1
            else:
                print(f"[FAIL] Section '{name}' not found")
                failed += 1

    # --- Test 3: Tables extracted correctly ---
    tables = soup.find_all("table")
    print(f"\nTotal tables: {len(tables)}")
    if len(tables) >= EXPECTED_TABLES_MIN:
        print(f"[PASS] Found {len(tables)} tables (expected >={EXPECTED_TABLES_MIN})")
        passed += 1
    else:
        print(f"[FAIL] Expected >={EXPECTED_TABLES_MIN} tables, got {len(tables)}")
        failed += 1

    # --- Test 4: Weapons table has expected structure ---
    weapons_elems = elements_between(elements, "Weapons")
    weapon_tables = [el for el in weapons_elems if el.name == "table"]
    if weapon_tables:
        rows = table_to_rows(weapon_tables[0])
        header = rows[0] if rows else []
        print(f"\nWeapons table: {len(rows)} rows, header: {header}")
        if any("Weapon" in h for h in header) and any("Dmg" in h for h in header):
            print("[PASS] Weapons table has expected headers")
            passed += 1
        else:
            print(f"[FAIL] Weapons table headers unexpected: {header}")
            failed += 1
        if len(rows) >= EXPECTED_WEAPONS_ROWS_MIN:
            print(f"[PASS] Weapons table has {len(rows)} rows (expected >={EXPECTED_WEAPONS_ROWS_MIN})")
            passed += 1
        else:
            print(f"[FAIL] Weapons table too few rows: {len(rows)} (expected >={EXPECTED_WEAPONS_ROWS_MIN})")
            failed += 1
    else:
        print("[FAIL] No tables found in Weapons section")
        failed += 2

    # --- Test 5: Spell entry structure ---
    spells_elems = elements_between(elements, "All Spells, in Alphabetical Order")
    if not spells_elems:
        for name in section_names:
            if "alphabetical" in name.lower():
                spells_elems = sections[name]
                break

    if spells_elems:
        spell_names = []
        for el in spells_elems:
            if el.name == "p":
                b = el.find("b")
                if b:
                    text = b.get_text(strip=True)
                    full_text = el.get_text()
                    if "Range:" in full_text:
                        spell_names.append(text)
        print(f"\nSpell entries found: {len(spell_names)}")
        if spell_names:
            print(f"  First 5: {spell_names[:5]}")
        if len(spell_names) >= EXPECTED_SPELLS_MIN:
            print(f"[PASS] Found {len(spell_names)} spells (expected >={EXPECTED_SPELLS_MIN})")
            passed += 1
        else:
            print(f"[FAIL] Expected >={EXPECTED_SPELLS_MIN} spells, got {len(spell_names)}")
            failed += 1
    else:
        print("[FAIL] Could not find spells section")
        failed += 1

    # --- Test 6: Monster stat block structure ---
    # Monsters span from PART 6 to PART 7
    part6_elems = elements_between_parts(elements, 6, 7)
    if part6_elems:
        monster_count = 0
        for el in part6_elems:
            if el.name == "table":
                rows = table_to_rows(el)
                for row in rows:
                    if row and "Armor Class:" in row[0]:
                        monster_count += 1
                        break
        print(f"\nMonster stat block tables: {monster_count}")
        if monster_count >= EXPECTED_MONSTERS_MIN:
            print(f"[PASS] Found {monster_count} monster stat tables (expected >={EXPECTED_MONSTERS_MIN})")
            passed += 1
        else:
            print(f"[FAIL] Expected >={EXPECTED_MONSTERS_MIN} monster tables, got {monster_count}")
            failed += 1
    else:
        print("[FAIL] Could not find PART 6 elements")
        failed += 1

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
