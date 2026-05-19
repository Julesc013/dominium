Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# org.dominium.core.signals.baseline

Purpose: Minimal signal fields, interfaces, and signal component primitives (button, lever, wire, lamp, counter).

Maturity: BOUNDED

Capabilities:
- org.dominium.core.signals
- org.dominium.core.signals.baseline

Dependencies (capability-level):
- org.dominium.core.units
- org.dominium.core.materials
- org.dominium.core.interfaces
- org.dominium.core.standards

Contents:
- `data/signals.json` (signal fields, interfaces, profiles)
- `data/fab_pack.json` (signal process families + parts)

Notes:
- Data-only and optional.
- Signals are symbolic, sampled, and event-driven.
- No assets required.
