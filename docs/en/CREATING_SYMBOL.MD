# Creating a Symbol Using the Primitives Menu

This guide describes the process of creating a new isometric symbol (SKEY) using geometric primitives in the OpenIso editor. As an example, we will create a Gate Valve symbol, which typically consists of two triangles connected at their vertices ("bowtie").

## Tool Location {#tool-location}

The drawing tools are located on the toolbar to the left of the main drawing area (canvas).
The main buttons we will need are:

*   ![Primitive Shapes](./images/menu_primitive.png) **Draw Primitive**: Button with a dropdown menu for selecting geometric shapes (triangle, circle, rectangle, etc.).
*   ![Connection Points](./images/point_arrive.png) **Draw Connection Point**: For adding pipe entry and exit points.
*   ![Spindle](./images/point_spindle.png) **Draw Spindle Connection Point**: For specifying the location of the actuator or handwheel.
*   ![Save](./images/save.png) **Save**: On the top toolbar for saving the created symbol.

---

## Step-by-Step Creation of a Gate Valve {#step-by-step-gate-valve}

### Step 1: Preparing a New SKEY {#step-1-prepare-skey}

1.  If you have an existing symbol open, right-click in the SKEY tree and select **Create New SKEY** (or clear the current input fields).
2.  In the properties panel on the right, enter the name of the new SKEY in the **SKEY Code** field (e.g., `VVFL`).
3.  Specify a description (e.g., `Flanged Gate Valve`) and select the fitting type (e.g., `Valve`).

### Step 2: Drawing the Symbol Body (Triangles) {#step-2-draw-body}

A gate valve is schematically depicted as two triangles touching at their vertices in the center.

1.  On the drawing toolbar, click the **Draw Primitive** button (or the arrow next to it).
2.  In the menu that appears, expand the **Basic Shapes** group.
3.  Select the **Triangle** tool.
4.  Draw the left part of the valve:
    *   Left-click on the canvas to place the first point (e.g., top-left corner).
    *   Click a second time to place the second point (e.g., bottom-left corner).
    *   Click a third time in the center of the symbol to close the triangle (vertex).
    *   *Tip: Use the grid and snapping for precision.*

5.  Repeat the action for the right part:
    *   The **Triangle** tool remains active.
    *   Click in the center of the symbol (at the same point where the first triangle ended).
    *   Click to place the top-right corner.
    *   Click to place the bottom-right corner.

Now you have the geometric base of the symbol in the form of a "bowtie".

### Step 3: Adding Connection Points {#step-3-connections}

The symbol needs to know where the pipe connects to it. Connection Points are used for this.

1.  Click the **Draw Connection Point** button on the toolbar.
    *   By default, **Arrive Point** (green) is selected.
2.  Click in the middle of the left base of the first triangle to place the entry point.
3.  To place the exit point, you need to change the point type (if it doesn't happen automatically):
    *   In the context menu (right-click) or by selecting the tool again, choose **Leave Point** (red).
4.  Click in the middle of the right base of the second triangle.

### Step 4: Adding a Spindle Point (Optional) {#step-4-spindle}

For valves and gate valves, it is important to indicate where the handwheel or actuator is located so that the program can orient it correctly when generating the isometric drawing.

1.  Click the **Draw Spindle Connection Point** button.
2.  Place the point in the center of the symbol (at the junction of the two triangles).
3.  If necessary, you can select the default spindle orientation.

### Step 5: Saving {#step-5-saving}

1.  Make sure the symbol looks correct.
2.  Click the **Save** button on the top toolbar.
3.  The new SKEY will appear in the symbol tree and will be saved to the database.

## Tips {#tips}

*   **Undo Actions**: If you make a mistake while drawing, use the **Undo** button or the `Ctrl+Z` shortcut.
*   **Editing**: You can select a drawn primitive with the **Select Element** tool and drag its nodes to change the shape.
*   **Precision**: Watch the coordinates in the status bar at the bottom of the window for precise point positioning.
