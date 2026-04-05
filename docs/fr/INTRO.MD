# OpenIso Introduction

**OpenIso** is a specialized graphical editor for creating and managing piping isometric symbols (SKEYs) used in computer-aided design (CAD) systems like AVEVA PDMS/E3D and Intergraph Smart 3D. It bridges the gap between raw data files and visual design, providing a user-friendly interface for engineers and designers.

## Purpose

The primary goal of OpenIso is to simplify the creation, editing, and management of symbol libraries. Instead of manually editing text files or using complex, heavy CAD suites just to tweak a symbol, users can launch OpenIso to quickly modify geometry, adjust connection points, and verify symbol integrity.

## Key Features

### 🎨 Vector Editing

- Draw complex shapes using primitives: Lines, Circles, Rectangles, Polygons.
- Precise control over coordinates and dimensions.
- Support for hatching and solid fills.

### 🔗 Connection Management

- Define standard connection types: **Arrive** (Inlet), **Leave** (Outlet), **Tee** (Branch), and **Spindle** (Actuator/Handle).
- Visual indicators for flow direction.

### 💾 Format Support

- **Import:** Read existing ASCII symbol definition files.
- **Export:** Generate compatible ASCII files for use in other systems.
- **Database:** Symbols are stored in a local SQLite database for quick access and versioning.

### 🌍 Cross-Platform

- Built with Python and Qt (PyQt6).
- Runs on **Linux** (Flatpak available) and **Windows**.
- Fully localized interface (English, Russian, French).

---

[Return to Index](./INDEX.MD)
