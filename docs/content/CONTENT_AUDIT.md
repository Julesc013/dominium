Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

Data content audit
==================

Scope: legacy `data/` content audit, retained as transition context.

Classification:
- PRESERVED: `capabilities/` (reference notes only; no content assumptions)
- PRESERVED: `defaults/` (profile presets; engine optional)
- PRESERVED: `law/` (placeholder documentation; no content assumptions)
- PRESERVED: `modules/` (documentation stubs; no content assumptions)
- PRESERVED: `registries/` (control/law registries; kept as system references)
- PRESERVED: `standards/` (documentation stubs; no content assumptions)
- ARCHIVED: `world/` -> moved to `data/archive/world/`
- ARCHIVED: `scenarios/` -> moved to `data/archive/scenarios/`
- MOVED: `packs/` -> `content/packs/` (canonical optional content packs)
- CURRENT: `archive/` (historical storage)

Notes:
- Legacy world and scenario data were archived to enforce the pack-based,
  capability-driven content model.
- Canonical base packs now live under `content/packs/` and are optional.
