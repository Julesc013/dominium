Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Launcher Scope (LAUNCH-0)

Status: binding.
Scope: launcher responsibilities, prohibitions, and orchestration rules.

## Responsibilities (MUST)
- Orchestrate installs, instances, profiles, run modes, and preflight checks.
- Treat CLI as canonical; TUI/GUI wrap CLI semantics.
- Enumerate installs, instances, and profiles on every surface.
- Generate a compat_report for every load/run/import/update action.
- Surface missing packs, compatibility mode, and refusal details.
- Require explicit confirmation for degraded/frozen/inspect-only runs.
- Provide one-click access to logs, replays, bugreports, and instance data paths.

## Prohibitions (MUST NOT)
- MUST NOT mutate simulation state.
- MUST NOT assume content is present.
- MUST NOT proceed without a compat_report.
- MUST NOT hide incompatibilities, refusals, or missing packs.
- MUST NOT auto-install or auto-remove packs without explicit consent.

## Read-only by default
- The launcher is read-only unless a user requests an explicit action.
- Any mutation (instance creation, pack add/remove, bundle import) is explicit,
  logged, and refusal-aware.

## Compatibility honesty
- The launcher never guesses. It uses compat_report output only.
- Compatibility modes are explicit: full, degraded, frozen, inspect-only, refuse.
- Degraded/frozen/inspect-only requires user confirmation.

## See also
- `docs/architecture/PRODUCT_SHELL_CONTRACT.md`
- `docs/architecture/COMPATIBILITY_MODEL.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`