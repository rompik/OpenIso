# Changelog

## 0.8.10 (2026-10-08)

### Improvements

- Fixed ASCII import so trailing blank lines do not discard the final symbol geometry.
- Corrected geometry centering and canvas serialization for rectangles, circles, and paths.
- Connected Undo and Redo controls to the scene history.
- Preserved Default, Off, and On values when editing symbol flags.
- Added regression tests for import, geometry, export, and editing behavior.

## 0.8.9 (2026-06-04)

Compared to the 0.8.8 baseline.

### New

- Added an Orientation group to the properties panel with four draw-orientation options: None, Always Vertical, All Primary, and User Defined.
- Added a new draw-orientation field to the Skey data model, database schema, and save/export payloads.

### Improvements

- Renamed the orientation-related UI widgets to mirror-oriented names for clarity in the codebase.
- Added database migration support so existing installations receive the new draw-orientation column automatically.
- Updated the symbol JSON preview so geometry entries are shown one per line instead of being wrapped across multiple lines.
- Reviewed SKEY endpoint connection types against the standard list and identified the current UI/schema gaps.

## 0.8.8 (2026-06-03)

Compared to the 0.8.6 baseline.

### New

- ASCII export now uses a single Strict Legacy mode only.
- Spindle assignment is now displayed in the symbol properties form and included in the JSON preview.

### Improvements

- Reworked ASC `501` record output to IsoAlgo-style fixed-width formatting (length 101).
- Reworked ASC `502` record output to strict fixed-width formatting (length 103) with deterministic zero-padding of trailing triplets.
- Improved interoperability of exported ASC files with legacy Intergraph/IsoAlgo-style parsers and symbol libraries.
- One-time database migration converts legacy `SpindlePoint` geometry entries to `ArrivePoint` for all spindle symbols.
- Spindle names are now synchronised from the reference `IsoAlgo.skey` file to the database on first run.
- Fixed a signal-ordering bug in the properties form where changing the symbol group could silently clear the spindle field before it was populated.

## 0.8.6 (2026-05-28)

Compared to the 0.8.5 baseline.

### New

- Added unsaved-status indication in the UI so changes are clearly visible before saving.
- Added a settings file and automatic creation of a user data folder.
- Added an option to change the path to the symbol database.

### Improvements

- Removed the separate "Save Skey" button from the interface.

## 0.8.5 (2026-05-26)

Compared to the 0.7.5 baseline.

### New

- Editor improvements: added a resizable properties panel, live synchronization of Skey properties, and a compact symbol JSON view.
- Extended symbol data model: added source metadata, release catalogs, and upstream version tracking for synchronization.
- Added and refined catalog synchronization tools, including conflict resolution flows.

### Improvements

- Reworked SQL scripts, database structure, and migrations to track source, release, and symbol versions.
- Improved help system behavior: correct path resolution for documentation and assets.
- Updated localization for `en`, `ru`, and `zh_CN`, including gettext catalogs.
- Improved packaging and publishing: CI/CD workflow, wheel/release builds, and behavior in packaged environments.
- Improved version and data path detection for both source runs and packaged application runs.

### Technical Changes

- Updated non-UI tests for services, database layer, importers, catalog synchronization, and schema behavior.
- Refreshed documentation and roadmap materials.
