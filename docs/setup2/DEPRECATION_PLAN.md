# Setup Legacy Deprecation Plan

## Phase 0: Coexistence (now)
- Setup2 is default for new installs.
- Legacy remains buildable and importable.

## Phase 1: New installs default to Setup2
- Legacy allowed for explicit opt-in only.
- All adapters and packaging default to Setup2.

## Phase 2: Legacy install-only
- Legacy cannot upgrade or repair.
- Setup2 import becomes the supported migration path.

## Phase 3: Legacy import-only
- Legacy binaries are archived and no longer distributed by default.
- Setup2 handles all operations.

## Advancement criteria
- Conformance suite passes across all supported platforms.
- Launcher handoff is validated with import fallback.
- Release gate enforces defaults and migration tests.

## Messaging
- Surface clear warnings when legacy paths are used.
- Provide explicit recovery steps and import commands.
