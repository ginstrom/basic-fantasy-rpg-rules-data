# Cleanup Phase Plan: Doc Builder Output Normalization

## Goal
Improve the generated JSON so it is easier and safer to consume programmatically, while preserving source meaning from the Basic Fantasy manual.

## Findings From Current Output

### 1) Category headers emitted as data rows
- `data/weapons.json` includes section labels as rows with empty attributes.
- Current header-like rows:
  - `Axes`
  - `Bows`
  - `Daggers`
  - `Swords`
  - `Hammers and Maces`
  - `Other Weapons`

### 2) Numeric ranges emitted as strings
- Hyphenated numeric ranges (e.g., `1-3`) appear in multiple files.
- Approximate occurrences by file:
  - `data/attack_bonus.json`: 30
  - `data/combat_tables.json`: 68
  - `data/magic_item_tables.json`: 223
  - `data/saving_throws.json`: 36
  - `data/spells.json`: 12
  - `data/treasure_types.json`: 2
  - `data/monsters.json`: 1 (`hit_dice: "1-1"`)

### 3) Comma-formatted numerics emitted as strings
- Numeric strings with thousands separators appear in:
  - `data/class_tables.json` (`points`): 57
  - `data/monsters.json` (`stat_block.xp`): 31
  - `data/vehicles.json` (`weight`, `cost_gp`): 3

## Proposed Cleanup Rules

### Rule A: Promote header rows to explicit categories
- For weapons (and any similar table), detect rows where the first column is non-empty and all value columns are empty.
- Do not emit these as normal item records.
- Emit category context directly on each item row.
- Canonical weapons shape example:
  - `{ "category": "Axes", "weapon": "Hand Axe", "price": "4 gp", "size": "S", "weight": "5", "dmg": "1d6" }`

### Rule B: Normalize integer range strings to structured values
- Convert exact integer ranges matching `^[0-9]+-[0-9]+$` into structured numeric data.
- Recommended canonical shape:
  - `{ "raw": "1-3", "min": 1, "max": 3, "values": [1,2,3] }`
- Only apply where field semantics are ordinal/integer ranges (levels, HD bands, percentile bands, etc.).
- Preserve original source string in `raw`.
- Edge handling:
  - Percentile wrap ranges like `98-00` should not become a simple `[98,99,100,0]`; represent as wrapped range metadata.
  - Non-range numeric notations like dice expressions (`1d6`) are out of scope.

### Rule C: Normalize comma-formatted numerics
- Convert strings matching `^[0-9]{1,3}(,[0-9]{3})+$` to integer values.
- Preserve source text separately only when downstream consumers need exact print formatting.
- Example:
  - `"1,000"` -> `1000`

## Implementation Plan

1. Add normalization utilities
- Create reusable helpers in the extraction pipeline:
  - `is_header_row(...)`
  - `parse_int_with_commas(...)`
  - `parse_numeric_range(...)`
  - `expand_closed_range(...)`
  - `parse_wrapped_percentile_range(...)`

2. Apply category/header normalization at table parse time
- Update weapon parser to treat section labels as category markers, not weapon rows.
- Backfill `category` on each weapon item.

3. Apply numeric normalization by schema-aware field map
- Use explicit field targets first (safe rollout), e.g.:
  - `class_tables.*[].points`
  - `monsters[].stat_block.xp`
  - `vehicles[].weight`, `vehicles[].cost_gp`
  - level/HD/range columns in attack/saving/combat/treasure tables
- Avoid global blind conversion initially.

4. Preserve backward compatibility
- Short term: keep existing raw strings beside normalized fields where risk exists.
- Add a clear deprecation note for old-only string fields if they will be removed later.

5. Expand tests
- Add fixture-based tests for:
  - header row stripping + category assignment
  - integer range parse + expansion
  - wrapped percentile range parse (`98-00`)
  - comma-number normalization
- Add regression tests ensuring dice notation and mixed text stay unchanged.

6. Regenerate and validate data
- Run build pipeline and compare before/after.
- Verify:
  - no header-only rows remain in item arrays
  - targeted numeric fields are numeric/structured
  - validation report remains pass/warning-equivalent or better

## Acceptance Criteria
- `data/weapons.json` has no category-only pseudo-items.
- Targeted comma numerics are normalized to integers.
- Targeted range fields are structured consistently and parseable.
- Existing non-target notations (`1d6`, textual rules prose) are unchanged.
- Tests cover each normalization rule and edge case.

## Risks and Mitigations
- Risk: accidental conversion of semantically textual values.
  - Mitigation: schema-targeted normalization and regression tests.
- Risk: consumer breakage from type changes.
  - Mitigation: dual-field transition (`raw` + normalized), documented migration.
- Risk: percentile wrap semantics mishandled.
  - Mitigation: dedicated parser branch and explicit test fixtures.
