# Phase 1.1: Extraction Validation Tightening

## Objective

Close the remaining quality gaps in the HTML extraction foundation by tightening
test expectations and documenting stable validation targets.

## Why This Exists

Phase 1 extraction is functionally complete, but one known validation gap remains:

- The spell-count expectation comment/target in `tests/test_phase1_extraction.py`
  is stale (`~65-70`) compared with current observed extraction (`97`).

## Tasks

- [x] Update spell-count expectation and pass criteria in
      `tests/test_phase1_extraction.py` to match validated manual content.
- [x] Add explicit baseline expectations for key extraction metrics
      (sections, tables, monster stat blocks) with reasonable tolerance.
- [x] Add a short extraction validation note documenting how to re-run and
      interpret phase 1 checks.
- [x] Re-run phase 1 tests and record final metrics in this file.

## Deliverables

- Updated `tests/test_phase1_extraction.py` with corrected expectations.
- Validation run notes with command and results.
- Stable acceptance thresholds for extraction-health regression checks.

## Exit Criteria

- Phase 1 test suite reflects current manual structure and no stale assumptions.
- All phase 1 checks pass with updated thresholds.
- Follow-up work is captured so later phases can rely on these checks.

## Validation Run (2026-02-09)

Command: `.venv/bin/python tests/test_phase1_extraction.py`

### Final Metrics (Release 142 HTML export)

| Metric                    | Observed | Threshold |
|---------------------------|----------|-----------|
| Top-level elements        | 3241     | —         |
| Section headers           | 396      | >= 390    |
| Tables                    | 296      | >= 290    |
| Weapons table rows        | 40       | >= 35     |
| Spell entries (alpha list)| 97       | >= 90     |
| Monster stat block tables | 200      | >= 190    |

**Result: 14/14 tests passed, 0 failed.**

Thresholds are set ~5% below observed values to tolerate minor HTML export
variations while still catching regressions.
