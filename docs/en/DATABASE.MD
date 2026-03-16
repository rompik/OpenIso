# OpenIso Database Architecture

OpenIso stores all project data in a local SQLite database (`data/database/openiso.db`). This file contains symbol definitions, groups, settings, and change history.

## 🗄️ Database Schema

The database is normalized to eliminate redundancy and uses foreign keys for relationships.

### `skeys` Table (Symbol Keys)
This is the master table storing metadata for each isometric symbol (SKEY).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, Auto | Unique ID of the symbol. |
| `name` | TEXT | UNIQUE | 4-char SKEY code (e.g., `VVFL`). |
| `skey_group_key` | TEXT | FK | Category (e.g., `valves`). |
| `skey_subgroup_key` | TEXT | FK | Sub-category (e.g., `gate`). |
| `orientation` | INTEGER | 0-3 | Visual orientation (Symmetrical, Asymmetrical). |
| `flow_arrow` | INTEGER | 0-2 | Direction flow arrow requirement. |
| `dimensioned` | INTEGER | 0-2 | Is the symbol dimensioned? |
| `tracing` | INTEGER | 0-2 | Heat tracing requirement. |
| `insulation` | INTEGER | 0-2 | Insulation requirement. |

### `geometry` Table
Stores the actual drawing primitives that make up the symbol.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Unique ID. |
| `skey_id` | INTEGER | FK to `skeys`. |
| `type` | TEXT | Primitive type: `Line`, `Circle`, `ArrivePoint`, etc. |
| `data` | TEXT | Serialized geometry data (JSON-like or comma-separated). |
| `transaction_id` | INTEGER | FK to `transactions` table. |

### `transactions` Table
Stores the history of changes. This allows undo/redo functionality and auditing.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Transaction ID. |
| `skey_id` | INTEGER | Symbol modified. |
| `action` | TEXT | `create`, `update`, `delete`. |
| `timestamp` | DATETIME | When the change occurred. |
| `user` | TEXT | Username who made the change. |

### `spindles` Table
Reusable definitions for valve handles/actuators.

| Column | Type | Description |
|---|---|---|
| `name` | TEXT | Unique name (e.g., `01SP`). |
| `description` | TEXT | Human-readable name (e.g., Vertical Handle). |

## 🔄 Data Flow

1.  **Loading:** When OpenIso starts, it queries `skeys` to populate the tree view.
2.  **Editing:** When a user opens a symbol, the application fetches the latest geometry based on the max `transaction_id` for that `skey_id`.
3.  **Saving:** Modifications create a *new* transaction and insert *new* records into `geometry`. Old records remain for history.

---
[Return to Index](INDEX.MD)
