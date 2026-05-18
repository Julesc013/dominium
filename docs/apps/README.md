Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Application Docs Index

Status: non-normative.
Canonical contracts live in `docs/architecture/CONTRACTS_INDEX.md`.

## Core Runtime
- `docs/apps/CLI_CONTRACTS.md` - CLI flags, build-info output, and refusal rules.
- `docs/apps/PRODUCT_BOUNDARIES.md` - product responsibilities and separation.
- `docs/apps/RUNTIME_LOOP.md` - shared loop phases and ownership.
- `docs/apps/TIMING_AND_CLOCKS.md` - clock domains and timing modes.
- `docs/apps/HEADLESS_AND_ZERO_PACK.md` - headless-first and zero-pack boot rules.
- `docs/apps/COMPATIBILITY_ENFORCEMENT.md` - version/protocol mismatch handling.
- `docs/apps/ARTIFACT_IDENTITY.md` - artifact identity fields and rules.

## UI Modes
- `docs/apps/UI_MODES.md` - unified `--ui` contract.
- `docs/apps/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` - canonical camera and blueprint commands.
- `docs/apps/TUI_MODE.md` and `docs/apps/GUI_MODE.md` - optional UI layers.
- `docs/apps/CLIENT_UI_LAYER.md` and `docs/apps/CLIENT_RENDERER_UI.md` - client UI shell.
- `docs/apps/NATIVE_UI_POLICY.md` and `docs/apps/TOOLS_UI_POLICY.md` - native UI boundaries.

## Observability And Security
- `docs/apps/READONLY_ADAPTER.md` - read-only engine/game adapter.
- `docs/apps/OBSERVABILITY_PIPELINES.md` - CLI/TUI/GUI observability outputs.
- `docs/apps/CLIENT_READONLY_INTEGRATION.md` - client read-only wiring.
- `docs/apps/TOOLS_OBSERVABILITY.md` - tool alignment on observability.
- `docs/apps/ENGINE_GAME_DIAGNOSTICS.md` - engine/game diagnostics policy.
- `docs/runtime/ui/FREECAM_MODES.md` - camera mode rules and refusal codes.
- `docs/runtime/ui/RENDERING_EPISTEMICS.md` - observation/memory render contract.
- `docs/security/CHEAT_THREAT_MODEL.md` - cheat classes and countermeasures.

## IDE Workflow
- `docs/apps/IDE_WORKFLOW.md` - IDE build/run guidance.
- `docs/apps/CLIENT_IDE_START_POINTS.md` - stable client extension points.

## TestX / APR Compliance
- `docs/apps/TESTX_INVENTORY.md` and `docs/apps/TESTX_COMPLIANCE.md`.
- Archived APR snapshots: see `docs/archive/app/` (archived).
