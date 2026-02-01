Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# UI System

Doc Version: 1

The launcher supports multiple UI backends while maintaining a strict separation between presentation and deterministic core behavior.

## Backends

Supported UI backends:
- `native`: platform-native UI
- `dgfx`: renderer-backed UI path
- `null`: headless/no-UI mode

Supported graphics modes:
- software (`soft`) where available
- `null` graphics for headless validation and CI

These must work in combinations including `--ui=null --gfx=null`.

## Separation of Concerns

- UI backends must not directly influence core decisions about instances, packs, or artifacts.
- UI selection is recorded in the audit log (selected backend + reason), but does not change instance state.
- All decisions that affect launch behavior must be represented as explicit inputs to the core (profiles/overrides/config).

## CLI and Profiles

The exhaustive CLI surface is defined in `docs/specs/SPEC_LAUNCHER_CLI.md`.

Profiles constrain backend choices deterministically; the core records any overrides and the final selection in audit.

See:
- `docs/specs/launcher/ARCHITECTURE.md`
- `docs/specs/SPEC_LAUNCHER_PROFILES.md`