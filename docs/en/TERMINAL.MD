# Terminal Commands Reference

The terminal allows you to control the symbol editor using text commands.

## Move
**Command:** `BY`
**Description:** Moves selected elements along the X and Y axes.
**Syntax:** `BY <Axis> <Value> [<Axis> <Value> ...]`
**Parameters:**
*   `<Axis>`: `X` or `Y`
*   `<Value>`: Number (offset in relative units)
**Examples:**
*   `BY X 0.1` — shift 0.1 to the right
*   `BY Y -0.2` — shift 0.2 down
*   `BY X 0.5 Y 0.5` — shift along both axes simultaneously

## Rotate
**Command:** `ROTATE`
**Description:** Rotates selected elements by a specified angle.
**Syntax:** `ROTATE [<Angle>]`
**Parameters:**
*   `<Angle>`: Number in degrees (default 90)
**Examples:**
*   `ROTATE` — rotate 90 degrees clockwise
*   `ROTATE 45` — rotate 45 degrees
*   `ROTATE -90` — rotate 90 degrees counterclockwise

## Clear
**Command:** `CLR`
**Description:** Deselects all elements on the canvas.
**Syntax:** `CLR`

## Help
**Command:** `HELP`
**Description:** Displays a list of available commands or brief help for a specific command.
**Syntax:** `HELP [<Command>]`
