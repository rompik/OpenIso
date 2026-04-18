# OpenIso Reference Guide

This document provides a comprehensive reference for all symbols used in OpenIso, including primitives, connection types, spindle handle orientations, and Symbol Keys (SKEYs).

## 1. Basic Primitives {#basic-primitives}

Primitive shapes are the fundamental drawing elements used to construct symbols.

| Icon | Name | Description | Visualization |
|:----:|:-----|:------------|:---------|
| `▬` | Line | A straight line segment | `-` |
| `▭` | Rectangle | A four-sided rectangle with 90° angles | `[]` |
| `⬜` | Square | A rectangle with equal sides | `[]` |
| `●` | Circle | A perfect circle | `O` |
| `◆` | Diamond | A rhombus shape (rotated square) | `<>` |
| `⬡` | Hexagon | Six-sided regular polygon | `⬡` |
| `△` | Triangle | Three-sided polygon | `^` |
| `⟿` | Spline | A curved line (Bezier spline) | `~` |
| `↻` | Scale | Scaling/resizing tool | `+` |
| `⇄` | Move | Movement/translation tool | `<->` |

## 2. Connection Types {#connection-types}

Connection types define how pipes are joined together.

| Code | Name | Description | Connection Method |
|:----:|:-----|:------------|:------------------|
| `PE` | Plain End | Pipe with plain/smooth end | Direct butt connection |
| `PL` | Plain | Plain connection without special features | Simple direct joint |
| `BW` | Butt Weld | Two pipes joined end-to-end and welded | Welded joint |
| `SW` | Socket Weld | Socket weld fitting connection | Pipe inserted into socket |
| `BE` | Beveled End | Pipe end with beveled edge for welding | Beveled edges |
| `TE` | Threaded End | Pipe with threaded end for screw connection | Threaded male/female connection |
| `THD` | Threaded | Threaded fitting connection | Full threaded connection |
| `FL` | Flange | Flanged connection for bolted joints | Bolted flange assembly |
| `CP` | Compression Plain | Plain fitting with compression connection | Compression cone connection |
| `SC` | Socket Compression | Socket compression fitting | Compression fitting in socket |

## 3. Spindle Handles {#spindle-handles}

Spindle orientations define the position and direction of valve handles or actuators.

| Code | Name | Description | Orientation |
|:----:|:-----|:------------|:-------------|
| `01SP` | Linear Vertical | Vertical line with horizontal branch | Single vertical orientation |
| `02SP` | Diamond | Diamond/square rotated pattern | Symmetrical pattern |
| `03SP` | L-Shaped | Right angle corner orientation | 90° bend |
| `04SP` | Oval Smooth | Smooth oval/elliptical shape | Curved profile |
| `05SP` | Cross | Cross-shaped orientation pattern | Four-way symmetrical |
| `06SP` | Triangle | Triangular handle shape | Three-point configuration |
| [See full list in application] | ... | ... | ... |

## 4. Symbol Catalog (SKEYs) {#symbol-catalog}

The following table lists common symbol keys available in the standard library.

| Group | Subgroup | Code | Symbol Image | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Valves** | Generic | `VV` | ![VV](./images/vv.png) | Vector Valve (Generic) |
| **Valves** | Gate | `VAVW` | ![VAVW](./images/vavw.png) | Butt Weld Gate Valve |
| **Valves** | Globe | `VAGL` | ![VAGL](./images/vagl.png) | Globe Valve |
| **Valves** | Check | `VACK` | ![VACK](./images/vack.png) | Check Valve |
| **Valves** | Ball | `VB` | ![VB](./images/vb.png) | Ball Valve |
| **Valves** | Diaphragm | `VD` | ![VD](./images/vd.png) | Diaphragm Valve |
| **Fittings** | Elbow | `ELBW` | ![ELBW](./images/elbw.png) | 90° Elbow Butt Weld |
| **Fittings** | Tee | `TEBW` | ![TEBW](./images/tebw.png) | Butt Weld Tee |
| **Fittings** | Reducer | `REDC` | ![REDC](./images/redc.png) | Concentric Reducer |
| **Fittings** | Reducer | `CPBW` | ![CPBW](./images/cpbw.png) | Concentric Reducer Butt Weld |
| **Flanges** | Weld Neck | `FLwn` | ![FLwn](./images/flwn.png) | Weld Neck Flange |
| **Flanges** | Blind | `FLBL` | ![FLBL](./images/flbl.png) | Blind Flange |
| **Flanges** | Flat Face | `FLFL` | ![FLFL](./images/flfl.png) | Flat Face Flange |
| **Flanges** | Raised | `FLRE` | ![FLRE](./images/flre.png) | Raised End Flange |
| **Olets** | Weldolet | `WELD` | ![WELD](./images/weld.png) | Weldolet |
| **Supports** | Hanger | `01HG` | ![01HG](./images/01hg.png) | Pipe Hanger |
| **Supports** | Guide | `GUID` | ![GUID](./images/guid.png) | Pipe Guide |
| **Supports** | Anchor | `ANCH` | ![ANCH](./images/anch.png) | Anchor Support |
| **Instruments** | Flow | `FLME` | ![FLME](./images/flme.png) | Flow Meter |
| **Instruments** | Gauge | `PR` | ![PR](./images/pr.png) | Pressure Gauge |
| **Instruments** | Orifice | `OP` | ![OP](./images/op.png) | Orifice Plate |
| **Special** | Cap | `KABW` | ![KABW](./images/kabw.png) | Cap Butt Weld |
| **Special** | Clamp | `CLMP` | ![CLMP](./images/clmp.png) | Clamp |
| **Special** | Trap | `TO` | ![TO](./images/to.png) | Trap Outlet |

> **Note:** Symbol images are placeholders and can be viewed directly in the application.

---

## 5. Symbol Anatomy {#symbol-anatomy}

Each SKEY symbol consists of the following components:

### Connection Points {#connection-points}

- **Arrive (Red)**: Primary inlet connection point.
- **Leave (Blue)**: Primary outlet connection point.
- **Tee (Magenta)**: Branch connection point.
- **Spindle (Dark Red)**: Valve handle/actuator orientation.

### Geometry Elements {#geometry-elements}

*   **Line:** Straight segment.
*   **Arc/Circle:** Curved segment or closed loop.
*   **Rectangle/Polygon:** Closed shapes that can be filled.
*   **Text:** Labels.

### Properties {#properties}

- **Orientation:**
    - *0 (Symmetrical):* Same when rotated 180°.
    - *1 (Non-Symmetrical):* Distinct inlet/outlet.
    - *2 (Reducers):* Handles size change.
    - *3 (Flanges):* Bolted connection handling.
- **Display Options:** Flow Arrow, Dimensioned, Tracing, Insulation visibility.

---
[Return to Index](./INDEX.MD)
