# Phase 1: Foundation

## Objective

Establish a reliable PDF extraction pipeline that can handle the manual's two-column layout and preserve reading order.

## Tasks

- [ ] Set up Python project dependencies (`pdfplumber`) and environment.
- [ ] Implement page-by-page extraction with coordinate data.
- [ ] Implement column splitting to convert two-column pages into sequential text.
- [ ] Test extraction quality on representative sample pages.

## Technical Notes

- Use `pdfplumber` as the primary extraction method.
- Detect the column gutter via x-position clustering.
- Remove repeated headers/footers and page-number noise during normalization.
- Use `pdftotext -layout` only as a validation fallback for spot checks.

## Deliverables

- Extraction utility for page/word/coordinate output.
- Column splitter utility.
- Initial extraction quality report from sample-page checks.

## Exit Criteria

- At least 10 representative pages parse in correct reading order.
- Spot checks against `pdftotext -layout` show no missing critical lines.
