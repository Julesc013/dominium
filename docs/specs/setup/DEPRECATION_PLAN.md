Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Legacy Deprecation Plan

## Phase 0: Coexistence (now)
- Setup is default for new installs.
- Legacy remains buildable and importable.

## Phase 1: New installs default to Setup
- Legacy allowed for explicit opt-in only.
- All adapters and packaging default to Setup.

## Phase 2: Legacy install-only
- Legacy cannot upgrade or repair.
- Setup import becomes the supported migration path.

## Phase 3: Legacy import-only
- Legacy binaries are archived and no longer distributed by default.
- Setup handles all operations.

## Advancement criteria
- Conformance suite passes across all supported platforms.
- Launcher handoff is validated with import fallback.
- Release gate enforces defaults and migration tests.

## Messaging
- Surface clear warnings when legacy paths are used.
- Provide explicit recovery steps and import commands.