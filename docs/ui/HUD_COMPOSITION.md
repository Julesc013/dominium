Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# HUD Composition (UX-1)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


HUDs are declarative data layouts. They must never mutate simulation state and must be togglable without affecting outcomes.

## Principles
- HUD elements are read-only projections of events, fields, and metrics.
- Elements are addressed by stable ids.
- Layouts are data-only and hot-swappable.

## Elements
Each element declares:
- `element_type` (text, meter, list, chart, etc.)
- `source` (event stream, field, metric)
- `position` (anchor + numeric coordinates)
- optional styling and visibility rules

## Schema
- `schema/hud_layout.schema`

## Example (Conceptual)
```
hud_id=org.dominium.hud.basic
hud_version=1.0.0
elements:
  - element_id=org.dominium.hud.clock
    element_type=text
    source_type=metric
    source_id=metric.tick
```

## References
- docs/ui/UX_OVERVIEW.md
