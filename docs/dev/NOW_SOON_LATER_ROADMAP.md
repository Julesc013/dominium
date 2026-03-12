Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# NOW / SOON / LATER Roadmap (Settings UX)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## NOW

- Settings ownership boundaries are documented and enforced.
- Client settings commands (`get/set/reset`) are available in canonical command graph.
- Launcher settings commands (`get/set`) are available.
- Setup settings commands (`get/set`) are available.
- Schema-defined settings files exist under `schema/settings/`.

## SOON

- Advanced accessibility hooks.
- Controller profile management.
- Guided setup wizard policy tuning.
- Launcher dependency graph and instance cloning UX.
- Server advanced rate limits and anti-cheat tuning.

SOON surfaces must remain explicitly marked as experimental/stub and refuse deterministically
when not implemented.

## LATER

- Rich theming/animation timelines.
- Cloud sync UX for launcher settings.
- Setup background update and advanced patch tuning.
- Server live policy dashboards.
