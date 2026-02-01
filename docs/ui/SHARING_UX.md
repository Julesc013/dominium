Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Sharing UX (SHARE0)

Status: binding.  
Scope: casual sharing UX for bundles.

## Casual UX (Primary)

Casual users see:
- Open
- Import
- Share

They do **not** see:
- pack IDs
- lockfiles
- instances

Advanced details are available behind a “Details…” panel.

## Import Flow (Casual)

1. User chooses bundle (drag-and-drop or Import…).
2. Launcher inspects bundle and shows compat_report summary:
   - compatible / degraded / inspect-only / refuse
3. Missing content is shown as human-readable summary.
4. User confirms if degraded mode is required.

## Share Flow (Casual)

1. User chooses artifact (save, replay, blueprint, modpack).
2. User selects “reference packs only” or “embed packs”.
3. Launcher generates bundle atomically.
4. User receives a single shareable bundle.

## Advanced Controls (Details Panel)

Power users can:
- inspect bundle internals
- extract embedded packs
- override pack resolution

These are exposed via tools, not default UI paths.