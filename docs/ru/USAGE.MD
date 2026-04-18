# OpenIso User Guide

This guide will walk you through the core functionality of the OpenIso editor.

## The Interface {#the-interface}

The main window is divided into three primary areas:

1. **Symbol Browser (Left Panel):** A hierarchical tree view of all available SKEYs, organized by Group and Subgroup (e.g., Valves -> Gate).
2. **Drawing Canvas (Center):** The main workspace where you draw geometry. It features a grid, zoom/pan controls, and visual feedback for coordinates.
3. **Properties Panel (Right Panel):** Displays attributes of the selected symbol (Name, Description, Orientation, Connection Type) or the selected primitive.

## detailed Operations {#detailed-operations}

### 📂 Navigating Symbols {#navigating-symbols}

- Expand the tree structure on the left to find a specific symbol.
- Double-click a symbol (SKEY code) to open it in the canvas.
- Right-click on a category to **Create New SKEY**.

### ✏️ Editing Geometry {#editing-geometry}

- **Draw Primitives:** Use the toolbar on the left to select drawing tools (Line, Circle, Rectangle, etc.).
  - _Click-and-drag_ to define dimensions.
  - _Hold Shift_ to constrain proportions (squares, circles).
- **Select & Move:** Use the **Select Tool** (Arrow icon) to click on existing shapes. Drag them to move or use the handles to resize.
- **Delete:** Select an element and press `Del` or `Backspace`.

### 🔗 Understanding Connections {#understanding-connections}

Piping symbols rely on specific connection points to define flow and orientation.

- **Arrive Point (Green):** Entrance of the pipe flow.
- **Leave Point (Red):** Exit of the pipe flow.
- **Tee Point (Blue):** Branch connection (for Tees/Olets).
- **Spindle Point (Yellow):** Orientation for valve handles.

> **Note:** Ensure connection points align perfectly with the geometry for accurate export.

### 💾 Saving Changes {#saving-changes}

- Click the **Save** button in the toolbar or press `Ctrl+S`.
- This commits changes to the local database and creates a transaction record.

---

[Return to Index](./INDEX.MD)

