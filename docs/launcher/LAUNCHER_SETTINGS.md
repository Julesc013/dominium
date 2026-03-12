Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Launcher Settings

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Launcher settings govern instance and session orchestration behavior.

## NOW (implemented)

- `active_instance`
- `default_instance`
- `pack_enablement` (per instance)
- `strict_compatibility_mode`
- `local_server_defaults`
- `update_check_policy`
- `log_verbosity`

## SOON (scaffolded)

- visual dependency graph
- instance cloning UX

## LATER (deferred)

- cloud sync
- visual diff dashboards

## Canonical Commands

- `launcher.settings.get`
- `launcher.settings.set`

Launcher settings do not mutate engine/game state directly.
