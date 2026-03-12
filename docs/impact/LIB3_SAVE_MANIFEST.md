Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# LIB3_SAVE_MANIFEST

## Changed

- `schema/lib/save_manifest.schema`
- `schema/lib/migration_event.schema`
- `schema/save.manifest.schema`
- `src/lib/save/__init__.py`
- `src/lib/save/save_validator.py`
- `tools/launcher/launcher_cli.py`

## Demand IDs

- `surv.knap_stone_tools`

## Contract Meaning

- selected saves are now first-class launcher inputs with manifest validation
- save open requires pinned contract bundle verification and pack lock alignment
- explicit save migration is available only through explicit launcher flags or direct helper invocation
- read-only fallback is opt-in per save via `allow_read_only_open`

## Unchanged

- simulation behavior and authoritative state mutation rules
- instance save associations remain references only
- generic share bundle topology remains compatible; full save bundle vendoring remains staged for LIB-6
