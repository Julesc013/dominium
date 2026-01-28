# Application Docs Index

Status: non-normative.
Canonical contracts live in `docs/architecture/CONTRACTS_INDEX.md`.

This index lists app-layer runtime, UI, and test contract documents.

## Core runtime
- `docs/app/CLI_CONTRACTS.md` - CLI flags, build-info output, and refusal rules.
- `docs/app/PRODUCT_BOUNDARIES.md` - product responsibilities and separation.
- `docs/app/RUNTIME_LOOP.md` - shared loop phases and ownership.
- `docs/app/TIMING_AND_CLOCKS.md` - clock domains and timing modes.
- `docs/app/HEADLESS_AND_ZERO_PACK.md` - headless-first and zero-pack boot rules.
- `docs/app/COMPATIBILITY_ENFORCEMENT.md` - version/protocol mismatch handling.
- `docs/app/ARTIFACT_IDENTITY.md` - artifact identity fields and rules.

## UI modes
- `docs/app/UI_MODES.md` - unified `--ui` contract.
- `docs/app/TUI_MODE.md` and `docs/app/GUI_MODE.md` - optional UI layers.
- `docs/app/CLIENT_UI_LAYER.md` and `docs/app/CLIENT_RENDERER_UI.md` - client UI shell.
- `docs/app/NATIVE_UI_POLICY.md` and `docs/app/TOOLS_UI_POLICY.md` - native UI boundaries.

## Observability and diagnostics
- `docs/app/READONLY_ADAPTER.md` - read-only engine/game adapter.
- `docs/app/OBSERVABILITY_PIPELINES.md` - CLI/TUI/GUI observability outputs.
- `docs/app/CLIENT_READONLY_INTEGRATION.md` - client read-only wiring.
- `docs/app/TOOLS_OBSERVABILITY.md` - tool alignment on observability.
- `docs/app/ENGINE_GAME_DIAGNOSTICS.md` - engine/game diagnostics policy.

## IDE workflow
- `docs/app/IDE_WORKFLOW.md` - IDE build/run guidance.
- `docs/app/CLIENT_IDE_START_POINTS.md` - stable client extension points.

## TestX / APR compliance
- `docs/app/TESTX_INVENTORY.md` and `docs/app/TESTX_COMPLIANCE.md`.
- Archived APR snapshots: `docs/archive/app/APR1_TESTX_COMPLIANCE.md`,
  `docs/archive/app/APR2_TESTX_COMPLIANCE.md`,
  `docs/archive/app/APR3_TESTX_COMPLIANCE.md`,
  `docs/archive/app/APR4_TESTX_COMPLIANCE.md`.
