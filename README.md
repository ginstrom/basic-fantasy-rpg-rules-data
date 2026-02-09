# basic-fantasy-rpg-rules-data

This project contains JSON data extracted from the Basic Fantasy RPG rules manual (Release 142 HTML export).

## Build prerequisites

To generate or regenerate data from source:

1. Download the LibreOffice source manual (`.odt`):
   - Direct file: https://basicfantasy.org/downloads/Basic-Fantasy-RPG-Rules-r142.odt
   - Downloads page (if direct hotlink changes): https://www.basicfantasy.org/downloads.html
2. Open the `.odt` in LibreOffice Writer and export/save it as HTML.
3. Place the exported HTML at `manual/Basic-Fantasy-RPG-Rules-r142.html`.

## Build and test

Use `make` targets from repo root:

```bash
make build
make test
```

- `make build` runs all generator scripts and writes JSON output in `data/`.
- `make test` runs extraction and data validation test scripts.

## Repository layout

- `scripts/`: scripts used to generate and update extracted data from the HTML manual.
- `data/`: generated JSON outputs.
- `manual/`: source manual files used for extraction.
- `src/`: parser and generation implementation.
- `tests/`: validation tests for extraction phases.

## Source

Data is derived from the Basic Fantasy RPG manual at https://www.basicfantasy.org/

## License

This project is licensed under CC BY-SA 4.0. See [LICENSE](LICENSE) for full terms and attribution details.

## Important Artwork Notice

Most artwork in the source manual is used by permission of original artists and is not covered by CC BY-SA terms for textual/maps/forms content. Redistributing the original manual "as is" may require removal of non-licensed artwork.
