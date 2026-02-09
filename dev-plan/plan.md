# Basic Fantasy RPG Rules PDF-to-JSON Parser — Development Plan

## Overview

Parse the **Basic Fantasy RPG 4th Edition (Release 142)** PDF manual (208 pages) into structured JSON data files suitable for use in apps, character builders, VTTs, etc.

**Source:** `manual/Basic-Fantasy-RPG-Rules-r142.pdf`
**License:** CC BY-SA 4.0 (text/data)

---

## 1. Text Extraction Strategy

### The Problem

The PDF uses a **two-column layout**. `pdftotext` (poppler) produces two different outputs:

| Mode | Lines | Behavior |
|------|-------|----------|
| Default (flow) | ~25,300 | Reads left column then right column per page, but **interleaves** paragraphs from both columns unpredictably |
| `-layout` | ~11,700 | Preserves spatial layout — left and right column text appears side-by-side on the same line |

**Layout mode** is more useful for parsing because column boundaries are preserved via whitespace. However, it means every line potentially contains content from *two* entries side-by-side.

### Recommended Approach

Use **`pdfplumber`** as the primary extraction pipeline, then:

1. **Page-by-page extraction** — extract words/chars with coordinates for each page to isolate headers/footers and reduce cross-page artifacts.
2. **Coordinate-based column split** — detect the column gutter using x-position clustering and split left/right column content into sequential reading order.
3. **Section-aware parsing** — apply section-specific parsers (spells, monsters, tables) to the normalized per-page text.

### Validation/Fallback

Use **`pdftotext -layout`** as a validation fallback:
- Compare sample pages against the `pdfplumber` output to catch dropped lines or ordering bugs.
- Use layout-mode text as a secondary parse source only when table or coordinate extraction fails.

---

## 2. Output File Structure

```
data/
├── races.json              # Dwarves, Elves, Halflings, Humans
├── classes.json            # Cleric, Fighter, Magic-User, Thief
├── class_tables.json       # Level progression, XP, HD, spells-per-day
├── saving_throws.json      # Saving throw tables by class & level
├── thief_abilities.json    # Thief skill percentages by level
├── equipment.json          # Adventuring gear, tools, supplies
├── weapons.json            # Weapons with cost, damage, weight, size, type
├── armor.json              # Armor types with cost, AC, weight
├── vehicles.json           # Vehicles and siege engines
├── spells.json             # All spells with full details
├── spell_lists.json        # Spell lists organized by class and level
├── monsters.json           # All monsters with stat blocks + descriptions
├── treasure_types.json     # Treasure type tables (A-T)
├── magic_items.json        # All magic items: weapons, armor, potions, etc.
├── magic_item_tables.json  # Random generation tables (d% rolls)
├── encounter_tables.json   # Wandering monster tables (dungeon + wilderness)
├── turning_undead.json     # Clerics vs. Undead table
├── attack_bonus.json       # Attack bonus table by class/level/HD
└── combat_tables.json      # Misc combat reference (cover, morale, etc.)
```

---

## 3. Data Schemas

### 3.1 `spells.json`

~65-70 spells. Each spell entry:

```jsonc
{
  "name": "Animate Dead",
  "reversible": false,        // true if marked with *
  "reverse_name": null,       // e.g. "Bane" for Bless
  "classes": [
    { "class": "Cleric", "level": 4 },
    { "class": "Magic-User", "level": 5 }
  ],
  "range": "30'",
  "duration": "special",
  "description": "The casting of this spell causes the mortal remains of...",
  // Optional fields present on some spells:
  "reverse_description": "...",  // if reversible
  "table": { ... }              // if spell includes a table (e.g. Confusion, Teleport, Reincarnate)
}
```

**Parsing challenge:** In the PDF, two spells appear side-by-side. The column splitter must cleanly separate them. Spell entries are identified by the pattern: `<Name> Range: <value>` on the same line (layout mode) or the class/level line like `Cleric 4, Magic-User 5`.

### 3.2 `monsters.json`

~200+ monster entries (many with variants). Each entry:

```jsonc
{
  "name": "Barkling",
  "armor_class": "15 (11)",    // string to preserve formatting like "(s)", "(m)"
  "hit_dice": "½ (1d4 hit points)",
  "attack_bonus": null,        // explicit if different from HD, e.g. "+9"
  "num_attacks": "1 bite or 1 weapon",
  "damage": "1d4 bite, 1d4 or by weapon",
  "movement": "20' Unarmored 40'",
  "num_appearing": "3d4, Wild 4d6, Lair 5d10",
  "save_as": "Normal Man",
  "morale": "7 (9)",
  "treasure_type": "P, Q each; C, K in lair",
  "xp": "10",
  "description": "Barklings are diminutive furry humanoids...",
  // Optional:
  "variants": [ ... ],         // for multi-column stat blocks (e.g. Ant Giant/Huge/Large)
  "age_table": { ... },        // for dragons
  "special_notes": "..."       // leaders, spellcasters, etc.
}
```

**Monster format types to handle:**
1. **Single stat block** — most common (Barkling, Ape, etc.)
2. **Multi-column variants** — one header, multiple columns (Ant Giant/Huge/Large, Beasts of Burden, Bear types)
3. **Dragon entries** — stat block + age progression table with hit dice, breath weapon, spells by level, damage by age
4. **Cross-references** — "See X on page Y" (Aurochs → Cattle)

### 3.3 `races.json`

```jsonc
{
  "name": "Dwarf",
  "description": "Dwarves are a short, stocky race...",
  "min_requirements": { "Constitution": 9 },
  "max_abilities": { "Charisma": 17 },
  "hit_die": "d6",
  "special_abilities": [
    "Darkvision 60'",
    "Detect shifting walls, new construction (1-2 on 1d6)"
  ],
  "saving_throw_bonuses": {
    "Death Ray or Poison": 4,
    "Magic Wands": 4,
    "Paralysis or Petrify": 4,
    "Dragon Breath": 3,
    "Spells": 4
  },
  "allowed_classes": ["Cleric", "Fighter", "Thief"],
  "allowed_combination_classes": []
}
```

### 3.4 `classes.json`

```jsonc
{
  "name": "Cleric",
  "description": "Clerics are those who have devoted themselves...",
  "prime_requisite": "Wisdom",
  "min_prime_requisite": 9,
  "hit_die": "d6",
  "armor_allowed": "any",
  "weapons_allowed": "blunt only (warhammer, mace, maul, club, quarterstaff, sling)",
  "abilities": ["Turn Undead", "Cast divine spells (from 2nd level)"]
}
```

### 3.5 `class_tables.json`

```jsonc
{
  "Cleric": [
    {
      "level": 1,
      "xp": 0,
      "hit_dice": "1d6",
      "spells": { "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0 }
    },
    {
      "level": 2,
      "xp": 1500,
      "hit_dice": "2d6",
      "spells": { "1": 1, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0 }
    }
    // ...levels 3-20
  ]
}
```

### 3.6 `weapons.json`

```jsonc
{
  "name": "Longsword",
  "cost_gp": 10,
  "size": "M",
  "weight_lbs": 4,
  "damage": "1d8",
  "type": "melee",
  // For missile weapons:
  "range_short": null,
  "range_medium": null,
  "range_long": null
}
```

### 3.7 `treasure_types.json`

```jsonc
{
  "type": "A",
  "category": "lair",
  "copper":   { "chance_pct": 50, "amount": "5d6", "unit": "hundreds" },
  "silver":   { "chance_pct": 60, "amount": "5d6", "unit": "hundreds" },
  "electrum": { "chance_pct": 40, "amount": "5d4", "unit": "hundreds" },
  "gold":     { "chance_pct": 70, "amount": "10d6", "unit": "hundreds" },
  "platinum": { "chance_pct": 50, "amount": "1d10", "unit": "hundreds" },
  "gems":     { "chance_pct": 50, "amount": "6d6" },
  "jewelry":  { "chance_pct": 50, "amount": "6d6" },
  "magic":    { "chance_pct": 30, "amount": "any 3" }
}
```

### 3.8 `magic_items.json`

```jsonc
{
  "name": "Potion of Healing",
  "category": "potion",
  "description": "Restores 1d6+1 hit points when consumed.",
  "duration": "instantaneous",
  "usable_by": "any"
}
```

Categories: `weapon`, `armor`, `potion`, `scroll`, `wand`, `staff`, `rod`, `ring`, `miscellaneous`

### 3.9 `encounter_tables.json`

```jsonc
{
  "dungeon": {
    "level_1": [
      { "roll": 1, "monster": "Bee, Giant" },
      { "roll": 2, "monster": "Goblin" }
      // ...12 entries per level
    ]
    // levels 1-8+
  },
  "wilderness": {
    "desert_barren": [
      { "roll": 2, "monster": "Dragon" }
      // ...
    ]
    // terrain types
  }
}
```

---

## 4. Parser Architecture

```
scripts/
├── parse_manual.py          # Main orchestrator / CLI entry point
├── extract_text.py          # PDF text extraction (pdfplumber-based)
├── column_splitter.py       # Two-column layout → sequential text
├── parsers/
│   ├── __init__.py
│   ├── spells.py            # Spell section parser
│   ├── monsters.py          # Monster section parser
│   ├── races.py             # Race section parser
│   ├── classes.py           # Class section parser
│   ├── equipment.py         # Equipment/weapons/armor parser
│   ├── treasure.py          # Treasure types + magic items parser
│   ├── tables.py            # Generic table parser (saving throws, attack bonus, etc.)
│   └── encounter_tables.py  # Wandering monster tables parser
├── utils.py                 # Shared helpers (dice notation, text cleanup, etc.)
└── validate.py              # Post-parse validation & cross-referencing
```

### Key Design Decisions

1. **Python** — best ecosystem for PDF parsing (`pdfplumber`), text processing, and JSON output.
2. **Page-range-based parsing** — each parser knows which PDF pages its section spans (from the TOC). This avoids cross-section contamination.
3. **Two-pass parsing** — first pass extracts raw text per section; second pass applies section-specific regex/heuristic parsers.
4. **Validation pass** — cross-references spells mentioned in class tables, monsters referenced in encounter tables, etc.

---

## 5. Parsing Strategy Per Section

### 5.1 Spells (pages 15-41, ~27 pages)

**Structure in PDF:**
- Pages 15-17: Spell lists organized by class/level (index)
- Pages 17-41: Alphabetical spell descriptions (two per page, side by side)

**Parsing approach:**
1. Extract spell index (pages 15-17) to build expected spell list
2. For each spell page, column-split left/right
3. Detect spell boundaries by matching: `<SpellName>` followed by `Range:` and `Duration:` lines
4. Extract class/level from the line like `Cleric 4, Magic-User 5`
5. Detect reversible spells by trailing `*` in name
6. Capture embedded tables (Confusion behavior table, Teleport accuracy table, Reincarnate form table)

**Regex patterns:**
- Spell header: `^([A-Z][a-zA-Z\s,'-]+)\*?\s+Range:\s+(.+)$`
- Class/level: `^(Cleric|Magic-User)\s+(\d),?\s*(?:(Cleric|Magic-User)\s+(\d))?`
- Duration: `^Duration:\s+(.+)$`

**Resilience rules:**
- If `Range:` is not on the header line, allow the next 1-2 lines to contain `Range:`/`Duration:`.
- Log and emit partial spell records (with a `parse_warnings` field) instead of dropping entries.

### 5.2 Monsters (pages 62-162, ~100 pages)

**Structure in PDF:**
- Page 62-63: Field definitions and explanations
- Pages 63-162: Alphabetical monster entries (two columns)

**Parsing approach:**
1. Detect stat block start by line matching `Armor Class:` with a value
2. Look backwards for the monster name (line(s) above the stat block)
3. Parse the fixed-order fields: Armor Class, Hit Dice, No. of Attacks, Damage, Movement, No. Appearing, Save As, Morale, Treasure Type, XP
4. Multi-column variants: detect when multiple values appear on the same stat line (e.g., `Giant  Huge  Large` above `Armor Class: 17  15  13`)
5. Dragon entries: after base stats, parse the age table grid
6. Cross-references ("See X on page Y"): store as a reference, don't duplicate data
7. Description text: everything between the last stat line and the next monster header

**Stat field regexes:**
- `Armor Class:\s+(.+)`
- `Hit Dice:\s+(.+)`
- `No\. of Attacks:\s+(.+)`
- `Damage:\s+(.+)`
- `Movement:\s+(.+)`
- `No\. Appearing:\s+(.+)`
- `Save As:\s+(.+)`
- `Morale:\s+(.+)`
- `Treasure Type:\s+(.+)`
- `XP:\s+(.+)`

**Resilience rules:**
- Do not require strict fixed-order fields; parse by label and allow missing/reordered labels.
- If a stat block is incomplete, keep the entry and attach `parse_warnings` for manual review.

### 5.3 Equipment & Weapons (pages 10-14)

**Structure:** Tabular data with clear column headers.

**Parsing approach:**
1. Use `pdfplumber` table detection to extract weapon/armor/equipment tables directly
2. Fall back to regex on layout text if table detection fails
3. Separate into: general equipment, weapons (melee + missile), armor, vehicles, siege engines

### 5.4 Treasure & Magic Items (pages 163-179)

**Structure:**
- Pages 163-165: Treasure type tables (A-T) — complex multi-column percentage tables
- Pages 166-168: Random generation tables (d% → item type)
- Pages 169-179: Magic item descriptions (prose format)

**Parsing approach:**
1. Treasure type tables: use `pdfplumber` table extraction (these are proper grid tables)
2. d% tables (potions, scrolls, wands, misc items): regex pattern `(\d{2}-?\d{0,2})\s+(.+)`
3. Magic item descriptions: split by bold/capitalized item name headers, capture prose description

### 5.5 Class & Race Data (pages 3-9)

**Parsing approach:**
1. Level progression tables: `pdfplumber` table extraction
2. Race descriptions: manually-bounded text regions based on known race names
3. Saving throw tables: table extraction from pages 60-61

### 5.6 Encounter Tables (pages 180-202)

**Parsing approach:**
1. Dungeon wandering monster tables: d12 roll → monster, organized by dungeon level (1-8+)
2. Wilderness encounter tables: 2d8 roll → monster, organized by terrain type
3. Regex: `(\d+)\s+(.+)` for numbered table rows

### 5.7 Combat Reference Tables

**Parsing approach:**
1. Extract combat-related reference tables (cover, concealment, morale, movement, and similar lookup tables) from their source pages.
2. Normalize each table to a common shape: `{ "table_name": "...", "rows": [...] }`.
3. Store in `combat_tables.json` with source page metadata for traceability.

---

## 6. Implementation Phases

### Phase 1: Foundation
- [ ] Set up Python project with dependencies (`pdfplumber`) and a `requirements.txt`
- [ ] Implement `extract_text.py` — page-by-page text extraction with coordinate data
- [ ] Implement `column_splitter.py` — reliable two-column separation
- [ ] Test extraction quality on a few sample pages

### Phase 2: Tables & Structured Data
- [ ] Parse equipment tables (weapons, armor, gear, vehicles)
- [ ] Parse class level progression tables
- [ ] Parse saving throw tables
- [ ] Parse thief abilities table
- [ ] Parse attack bonus table
- [ ] Parse turning undead table
- [ ] Output: `weapons.json`, `armor.json`, `equipment.json`, `vehicles.json`, `class_tables.json`, `saving_throws.json`, `thief_abilities.json`, `attack_bonus.json`, `turning_undead.json`

### Phase 3: Spells
- [ ] Parse spell index (class/level organization)
- [ ] Parse all individual spell entries
- [ ] Handle reversible spells and embedded tables
- [ ] Output: `spells.json`, `spell_lists.json`

### Phase 4: Monsters
- [ ] Parse standard single-column stat blocks
- [ ] Handle multi-column variant monsters
- [ ] Handle dragon age tables
- [ ] Handle cross-references
- [ ] Capture description text
- [ ] Output: `monsters.json`

### Phase 5: Treasure & Magic Items
- [ ] Parse treasure type tables
- [ ] Parse random generation tables (d%)
- [ ] Parse magic item descriptions by category
- [ ] Output: `treasure_types.json`, `magic_items.json`, `magic_item_tables.json`

### Phase 6: Races, Classes & Encounters
- [ ] Parse race data
- [ ] Parse class descriptions
- [ ] Parse dungeon encounter tables
- [ ] Parse wilderness encounter tables
- [ ] Parse combat reference tables
- [ ] Output: `races.json`, `classes.json`, `encounter_tables.json`, `combat_tables.json`

### Phase 7: Validation & Polish
- [ ] Cross-reference validation (spells in spell lists match spell entries, monsters in encounter tables exist in monsters.json, etc.)
- [ ] Spell-check and text cleanup (remove artifacts from PDF extraction)
- [ ] Consistent formatting (trailing whitespace, unicode normalization)
- [ ] Generate `data/README.md` describing the schema

### Phase Exit Criteria

- **Phase 1 exit:** At least 10 representative pages parse with correct reading order and no missing lines in spot checks against `pdftotext -layout`.
- **Phase 2 exit:** All planned table JSON files are generated and parse as valid JSON.
- **Phase 3 exit:** Spell count is within expected range (~65-70), with class/level metadata present for all entries.
- **Phase 4 exit:** Monster count is within expected range (~200+), with required core stat fields present in most entries and warnings logged for exceptions.
- **Phase 5 exit:** Treasure, random generation, and magic item outputs all generated with non-empty records.
- **Phase 6 exit:** Race/class/encounter/combat outputs generated with expected top-level keys and row counts.
- **Phase 7 exit:** Cross-reference checks pass with zero unresolved critical references; remaining warnings are documented.

---

## 7. Known Parsing Challenges

| Challenge | Severity | Mitigation |
|-----------|----------|------------|
| Two-column text interleaving | High | Use `pdfplumber` with x-coordinate column splitting |
| Monster variants in multi-column layout | High | Detect multiple value columns; build variant sub-entries |
| Dragon age tables | Medium | Special-case parser for dragon entries |
| Spell text interleaved between two spells | High | Column splitter + spell-boundary detection via `Range:`/`Duration:` headers |
| Table extraction from PDF | Medium | `pdfplumber.extract_tables()` with fallback to regex |
| Page headers/footers contaminating text | Low | Strip lines matching `^BASIC FANTASY RPG$`, `^MONSTERS$`, `^SPELLS$`, `^\d+$` |
| Inconsistent whitespace in extracted text | Low | Normalize whitespace in post-processing |
| Magic item descriptions vary in length | Low | Parse until next capitalized item name header |
| Cross-references between sections | Low | Store as references; validate in Phase 7 |

---

## 8. Dependencies

```
python >= 3.10
pdfplumber >= 0.10
```

No other external dependencies needed. Standard library `json`, `re`, `pathlib` suffice for the rest.

---

## 9. Running the Parser

```bash
# Install dependencies
pip install pdfplumber

# Run full parse
python scripts/parse_manual.py manual/Basic-Fantasy-RPG-Rules-r142.pdf --output data/

# Run a single section
python scripts/parse_manual.py manual/Basic-Fantasy-RPG-Rules-r142.pdf --section spells --output data/

# Validate output
python scripts/validate.py data/
```

---

## 10. Success Criteria

- All ~65-70 spells parsed with name, class/level, range, duration, description
- All ~200+ monsters parsed with complete stat blocks and descriptions
- All equipment/weapon/armor tables accurately captured
- All level progression tables for 4 classes captured
- All treasure type tables and magic item descriptions captured
- Encounter tables for all dungeon levels and wilderness terrain types
- Validation pass reports zero missing cross-references
- JSON files are valid, consistently formatted, and human-readable
