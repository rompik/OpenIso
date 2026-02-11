# OpenIso Symbols Reference

This document provides a comprehensive reference for all symbols used in OpenIso, including primitives, connection types, spindle handle orientations, and Symbol Keys (SKEYs).

---

## Table of Contents

1. [Basic Primitives](#basic-primitives)
2. [Connection Types](#connection-types)
3. [Spindle Handles](#spindle-handles)
4. [Symbol Keys (SKEYs)](#symbol-keys-skeys)
   - [Valves](#valves)
   - [Fittings & Reducers](#fittings--reducers)
   - [Instruments](#instruments)
   - [Supports](#supports)
   - [Flanges](#flanges)
   - [Special Components](#special-components)

---

## Basic Primitives

Primitive shapes are the fundamental drawing elements used to construct symbols. These are vector-based and can be filled with colors or drawn with strokes.

| Icon | Name | Description | Geometry | SVG Source |
|:----:|:-----|:------------|:---------|:-----------|
| `▬` | Line | A straight line segment | Single line element | `primitives/line.svg` |
| `▭` | Rectangle | A four-sided rectangle with 90° angles | Single rectangle element | `primitives/rectangle.svg` |
| `⬜` | Square | A rectangle with equal sides | Single square element | `primitives/square.svg` |
| `●` | Circle | A perfect circle | Single circle element | `primitives/circle.svg` |
| `◆` | Diamond | A rhombus shape (rotated square) | Single polygon element | `primitives/diamond.svg` |
| `⬡` | Hexagon | Six-sided regular polygon | Single polygon element | `primitives/hexagon.svg` |
| `△` | Triangle | Three-sided polygon | Single polygon element | `primitives/triangle.svg` |
| `⟿` | Spline | A curved line (Bezier spline) | 3 path elements | `primitives/spline.svg` |
| `↻` | Scale | Scaling/resizing tool | 8 geometric elements | `primitives/scale.svg` |
| `⇄` | Move | Movement/translation tool | 6 geometric elements | `primitives/move.svg` |

---

## Connection Types

Connection types define how pipes are joined together. Each type represents a specific method of connecting two pipe segments or fitting ends.

| Code | Name | Description | Connection Method | Geometry | SVG Source |
|:----:|:-----|:------------|:------------------|:---------|:-----------|
| `PE` | Plain End | Pipe with plain/smooth end | Direct butt connection | 2 line elements | `connections/pe.svg` |
| `PL` | Plain | Plain connection without special features | Simple direct joint | 2 line elements | `connections/pl.svg` |
| `BW` | Butt Weld | Two pipes joined end-to-end and welded | Welded joint with perpendicular lines | 1 line + 1 circle element | `connections/bw.svg` |
| `SW` | Socket Weld | Socket weld fitting connection | Pipe inserted into socket and welded | 2 line + 1 circle elements | `connections/sw.svg` |
| `BE` | Beveled End | Pipe end with beveled edge for welding | Beveled edges for V-groove welds | 4 line elements | `connections/be.svg` |
| `TE` | Threaded End | Pipe with threaded end for screw connection | Threaded male/female connection | 4 line elements | `connections/te.svg` |
| `THD` | Threaded | Threaded fitting connection | Full threaded connection | 4 line elements | `connections/thd.svg` |
| `FL` | Flange | Flanged connection for bolted joints | Bolted flange assembly | 3 line elements | `connections/fl.svg` |
| `CP` | Compression Plain | Plain fitting with compression connection | Compression cone connection | 3 line elements | `connections/cp.svg` |
| `SC` | Socket Compression | Socket compression fitting | Compression fitting in socket | 4 line elements | `connections/sc.svg` |

---

## Spindle Handles

Spindle orientations define the position and direction of valve handles or actuators. These are critical for 3D visualization and maintenance documentation.

| Code | Name | Description | Orientation | Geometry Elements | SVG Source |
|:----:|:-----|:------------|:-------------|:------------------|:-----------|
| `01SP` | Linear Vertical | Vertical line with horizontal branch | Single vertical orientation | 3 line + 1 spindle point | `spindles/01SP.svg` |
| `02SP` | Diamond | Diamond/square rotated pattern | Symmetrical pattern | 5 line + 1 spindle point | `spindles/02SP.svg` |
| `03SP` | L-Shaped | Right angle corner orientation | 90° bend | 3 line + 1 spindle point | `spindles/03SP.svg` |
| `04SP` | Oval Smooth | Smooth oval/elliptical shape | Curved profile | 15 line + 1 spindle point | `spindles/04SP.svg` |
| `05SP` | Cross | Cross-shaped orientation pattern | Four-way symmetrical | 3 line + 1 spindle point | `spindles/05SP.svg` |
| `06SP` | Triangle | Triangular handle shape | Three-point configuration | 4 line + 1 spindle point | `spindles/06SP.svg` |
| `07SP` | Shaft Complex | Complex shaft with multiple branches | Multi-branch actuator | 13 line + 1 spindle point | `spindles/07SP.svg` |
| `08SP` | Dual Block | Two rectangular blocks arrangement | Double configuration | 6 line + 1 spindle point | `spindles/08SP.svg` |
| `09SP` | Zigzag | Zigzag waveform pattern | Vibrating/oscillating handle | 8 line + 1 spindle point | `spindles/09SP.svg` |
| `10SP` | Rectangular | Large rectangular box shape | Fixed rectangular actuator | 7 line + 1 spindle point | `spindles/10SP.svg` |
| `11SP` | Circular | Smooth circular/round handle | Rotational symmetry | 13 line + 1 spindle point | `spindles/11SP.svg` |
| `12SP` | Rounded Top | Rounded rectangular with arch | Domed/bulged top | Custom geometry | `spindles/12SP.svg` |
| `13SP` | Tapered | Tapered/conical shape | Gradual width reduction | Custom geometry | `spindles/13SP.svg` |
| `14SP` | Coupled | Double-linked coupling shape | Connected dual segments | Custom geometry | `spindles/14SP.svg` |
| `15SP` | Extended | Extended shaft with offset | Displaced actuator | Custom geometry | `spindles/15SP.svg` |
| `16SP` | T-Shaped | T-joint configuration | Cross with offset | Custom geometry | `spindles/16SP.svg` |

---

## Symbol Keys (SKEYs)

Symbol Keys represent complete piping components with defined connection points (Arrive, Leave, Tee, Spindle) and geometry.

### Valves

Valves control flow and include various types for different applications.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `AV` | Angle Valve | 90° flow direction change | Flow control | Arrive, Leave | 7 elements |
| `VV` | Vector Valve | Multi-directional flow control | Universal | Arrive, Leave, Tee | Variable |
| `CK` | Check Valve | One-way flow prevention | Anti-backflow | Arrive, Leave | Variable |
| `VB` | Ball Valve | Spherical closure element | Isolation | Arrive, Leave | Variable |
| `VD` | Diaphragm Valve | Diaphragm-based throttling | Flow control | Arrive, Leave | Variable |

### Fittings & Reducers

Fittings connect pipe segments; reducers change pipe sizes.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `CPBW` | Concentric Reducer Butt Weld | BW connector with size reduction | Size Change | Arrive, Leave | 10 elements |
| `ELBW` | Elbow Butt Weld | 90° direction change with BW | Direction Change | Arrive, Leave | Variable |
| `TEBW` | Tee Butt Weld | T-junction with BW connections | Branch | Arrive, Leave, Tee | Variable |
| `REDC` | Reducer Coupling | Reducing coupling fitting | Size Change | Arrive, Leave | Variable |

### Instruments

Instruments provide measurement and indication functions.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `OP` | Orifice Plate | Pressure drop/flow measurement | Measurement | Arrive, Leave | 11 elements |
| `PR` | Pressure Gauge | Pressure measurement device | Measurement | Arrive | Variable |
| `DR` | Drain Valve | System drainage point | Drainage | Arrive, Leave | Variable |
| `CV` | Control Valve | Automatic flow control | Regulation | Arrive, Leave | Variable |
| `CA` | Cavity | Void/pocket in assembly | Special | Arrive, Leave | Variable |

### Supports

Supports provide structural framework and pipe hangers.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `01HG` | Pipe Hanger | Suspended pipe support | Vertical Support | Arrive, Leave | 5 elements |
| `ANCH` | Anchor | Fixed point anchor | Fixed Point | Arrive, Leave | Variable |
| `DUCK` | Duck Foot | Lateral support bracket | Lateral Support | Arrive, Leave | Variable |
| `GUID` | Guide | Directional guidance support | Guide | Arrive, Leave | Variable |
| `SKID` | Skid Block | Horizontal support block | Horizontal Support | Arrive, Leave | Variable |

### Flanges

Flanges provide bolted connections between components.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `FLBL` | Flange Blind | Sealing plate flange | Sealed Joint | Arrive | 7 elements |
| `FLFL` | Flange Flat Face | Flat surface flange | Standard Joint | Arrive, Leave | 7 elements |
| `FLLB` | Flange Long Bearing | Extended bearing flange | Long Format | Arrive, Leave | Variable |
| `FLRC` | Flange Raised Center | Raised profile flange | Specialty Joint | Arrive, Leave | Variable |
| `FLRE` | Flange Raised End | Raised edge flange | Raised Profile | Arrive, Leave | Variable |
| `FLSJ` | Flange Socket Joint | Socket type flange | Socket Connection | Arrive, Leave | 7 elements |

### Special Components

Specialized components for unique applications.

| SKEY | Name | Description | Type | Connections | Total Geometry |
|:----:|:-----|:------------|:-----|:------------|:---------------|
| `KABW` | Cap Butt Weld | End cap with BW connection | Closure | Arrive | 12 elements |
| `KACP` | Cap Compression | End cap with compression fit | Closure | Arrive | Variable |
| `CLMP` | Clamp | Mechanical joining clamp | Coupling | Arrive, Leave | 6 elements |
| `CLVT` | Clamp Viton | PTFE-lined clamped joint | Specialty Coupling | Arrive, Leave | Variable |
| `CLGY` | Clamp Assembly | Multi-component clamp | Complex Coupling | Arrive, Leave | Variable |
| `CLVR` | Clamp Venturi | Venturi-type clamp | Flow Device | Arrive, Leave | Variable |
| `TO` | Trap Outlet | Condensate trap outlet | Drainage | Arrive, Leave | 6 elements |
| `TI` | Trap Inlet | Condensate trap inlet | Drainage | Arrive, Leave | Variable |
| `TA` | Trap Assembly | Complete trap unit | Drainage | Arrive, Leave, Tee | Variable |

---

## Symbol Anatomy

Each SKEY symbol consists of the following components:

### Connection Points

- **Arrive (Red)**: Primary inlet connection point - where flow enters the component
- **Leave (Blue)**: Primary outlet connection point - where flow exits the component
- **Tee (Magenta)**: Branch connection point - used for T-junctions and branch connections
- **Spindle (Dark Red)**: Orientation point - indicates valve handle or actuator position

### Geometry Elements

Symbols are constructed from basic geometric elements:

```
StartPoint: Defines an arrival connection point
EndPoint: Defines a leave connection point
TeePoint: Defines a branch connection point
SpindlePoint: Defines the spindle orientation point
Line: Straight line segment from (x1,y1) to (x2,y2)
Arc: Curved line segment with center and radius
Circle: Filled or unfilled circular area
Rectangle: Filled rectangular area
Polygon: Custom multi-point closed shape
Text: Alphanumeric label
```

### Geometry Format (ASCII)

The geometry is stored in ASCII format:

```
StartPoint: x0=<value> y0=<value>
Line: x1=<x1_value> y1=<y1_value> x2=<x2_value> y2=<y2_value>
Circle: x=<x_value> y=<y_value> r=<radius>
Arc: x=<center_x> y=<center_y> r=<radius> startAngle=<start> sweepAngle=<sweep>
```

---

## Symbol Properties

Each symbol can have the following properties:

### Orientation

- **Symmetrical (0)**: Component appears same when rotated 180°
- **Non-Symmetrical (1)**: Component has distinct inlet/outlet orientation
- **Reducers (2)**: Component changes pipe diameter
- **Flanges (3)**: Bolted flange connection

### Display Options

- **Flow Arrow**: Show/hide flow direction arrows (Default, Off, On)
- **Dimensioned**: Show/hide dimension lines (Default, Off, On)
- **Tracing**: Show/hide component outline tracing (Default, Off, On)
- **Insulation**: Show/hide insulation wrap visualization (Default, Off, On)

---

## File Structure

Symbol files are organized by type:

```
data/icons/
├── primitives/          # Basic drawing shapes
│   ├── line.svg
│   ├── rectangle.svg
│   ├── circle.svg
│   ├── square.svg
│   ├── diamond.svg
│   ├── hexagon.svg
│   ├── triangle.svg
│   └── spline.svg
├── connections/         # Pipe connection types
│   ├── be.svg          # Beveled End
│   ├── bw.svg          # Butt Weld
│   ├── cp.svg          # Compression Plain
│   ├── fl.svg          # Flange
│   ├── pe.svg          # Plain End
│   ├── pl.svg          # Plain
│   ├── sc.svg          # Socket Compression
│   ├── sw.svg          # Socket Weld
│   ├── te.svg          # Threaded End
│   └── thd.svg         # Threaded
├── spindles/            # Valve handle orientations
│   ├── 01SP.svg through 16SP.svg
│   └── icons.qrc        # Qt resource file
└── skeys/               # Symbol Key visual references
    └── structure.svg    # SKEY anatomy diagram

data/settings/
├── OpenIso.json         # SKEY data with geometry definitions
├── IsoAlgo.skey         # Algorithm configuration
└── ...

po/                      # Localization files
├── messages.pot         # Translation template
├── en.po, fr.po, ru.po  # Language files
└── ...
```

---

## Total Symbol Count

- **Primitives**: 10 basic shapes
- **Connection Types**: 10 types
- **Spindle Orientations**: 16 variants
- **Symbol Keys (SKEYs)**: 250+ components across 20+ categories

---

## See Also

- [Usage Guide](docs/en/USAGE.MD) - How to use OpenIso editor
- [Terminal Commands Reference](docs/en/TERMINAL.MD) - Command-line operations
- [Installation Guide](docs/en/INSTALL.MD) - Setup instructions
- [Contributing Guide](docs/en/CONTRIBUTING.MD) - How to contribute
