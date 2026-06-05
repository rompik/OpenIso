# What's New

Complete history of user-facing changes in OpenIso.

## Version 0.8.8 (2026-06-03)

### New

- ASCII export now works in one mode only: Strict Legacy.

### Improvements

- Updated ASC `501` record formatting to IsoAlgo-style fixed-width output.
- Updated ASC `502` record formatting to strict fixed-width output with stable zero-padding.
- Improved compatibility of exported ASC symbols with legacy Intergraph/IsoAlgo libraries.

## Version 0.8.6 (2026-05-28)

### New

- Added unsaved-status indication in the editor.
- Added a user settings file and automatic creation of a user workspace folder.
- Added an option to change the symbols database path.

### Improvements

- Removed the separate Save Skey button from the toolbar.

## Version 0.8.5 (2026-05-26)

### New

- Improved editor workflow with a resizable properties panel, live Skey properties synchronization, and a compact symbol JSON view.
- Extended the symbol data model with source metadata, release catalogs, and version tracking for synchronization.
- Added and refined catalog synchronization tools, including conflict handling.

### Improvements

- Improved help behavior with correct documentation and asset path resolution.
- Updated localization for English, Russian, and Simplified Chinese.
- Improved data-path and version detection for both source runs and packaged application runs.
