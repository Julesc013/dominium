Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# Consistency Audit Report (CA-0)

## Executive Summary
- Entry gates PASS on `15acbd4537fd821813730f0638a10938ead922cd`:
  - `python scripts/ci/check_repox_rules.py --repo-root .`
  - `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game`
  - `cmake --build out/build/vs2026/verify --config Debug --target testx_all`
- Repository is broadly enforceable but not fully internally consistent.
- Detected: 3 `VIOLATION`, 11 `RISK`, 14 `INFO`.
- High-confidence gaps are concentrated in enforcement depth (token checks vs semantic checks) and doc/implementation drift.

## Axis A - Canon vs Code
Status: `partially_enforced`

- `INFO`: Determinism and build gates are enforced by TestX + strict build targets (`tests/*`, `out/build/vs2026/verify` targets).
- `INFO`: Capability-only token ban is enforced outside docs via RepoX (`scripts/ci/check_repox_rules.py`, `check_forbidden_legacy_gating_tokens`).
- `RISK`: Process-only mutation enforcement is mostly token-driven and root-limited (`tests/invariant/process_only_mutation_tests.py`; scans `engine`, `game` for specific symbols only).
- `RISK`: Process runtime ID enforcement scans only `engine/modules/world` and `game/rules`, so mutation paths outside those roots are not covered (`scripts/ci/check_repox_rules.py`, `check_process_runtime_literals`).

## Axis B - Docs vs Implementation
Status: `partially_enforced`

- `VIOLATION`: `docs/architecture/CAPABILITY_ONLY_CANON.md` forbids stage/progression identifiers outside planning language, but `docs/CAPABILITY_STAGES.md` and `docs/TESTX_STAGE_MATRIX.md` still prescribe runtime stage rules and identifiers.
- `RISK`: `docs/app/COMMAND_GRAPH_CAMERA_AND_BLUEPRINT.md` claims mode-specific capability checks for memory/observer camera modes, but command metadata currently encodes only `ui.camera.mode.embodied` for `camera.set_mode` (`libs/appcore/command/command_registry.c`).
- `RISK`: `docs/security/CHEAT_THREAT_MODEL.md` and `docs/security/CHEATING_AND_VERIFICATION.md` are near-duplicate normative surfaces with overlapping authority claims.

## Axis C - Schemas vs Runtime Expectations
Status: `partially_enforced`

- `INFO`: Pack manifest schema is capability-first (`schema/pack_manifest.schema`, `schema_version: 2.3.0`), and validator rejects legacy stage keys (`tools/pack/pack_validate.py`).
- `INFO`: Explicit migration routes exist and are deterministic for pack manifest versions (`tools/schema_migration/schema_migration_runner.py`, `schema/SCHEMA_MIGRATION_REGISTRY.json`).
- `RISK`: RepoX schema migration checks are structural; they do not prove complete runtime call-site coverage of explicit migration invocation.
- `RISK`: `repo/canon_state.json` booleans (`validated_by`) are asserted static content, not dynamic proof of current-run success.

## Axis D - Schemas vs Data Packs
Status: `partially_enforced`

- `INFO`: Pack manifests are validated for required capability fields and legacy stage-key rejection (`tools/pack/pack_validate.py`, RepoX pack capability checks).
- `RISK`: Capability overlap/conflict surfaces are present and non-fatal (`python tools/pack/capability_inspect.py --repo-root . --format json` reports conflicts while returning `"ok": true`).
- `RISK`: Current guardrail allows conflicting capability providers unless external lockfile policy resolves them correctly.

## Axis E - Capabilities vs Enforcement
Status: `partially_enforced`

- `INFO`: Core pack capability gates are enforced (`requires_capabilities`, `provides_capabilities`, `entitlements`).
- `VIOLATION`: Declared capabilities are not consistently enforced in runtime:
  - Declared in `data/capabilities/app_ui_camera_blueprint.json`: `ui.camera.mode.memory`, `ui.camera.mode.observer`, `tool.observation.stream`, `tool.memory.read`.
  - Not used by command metadata or runtime capability checks (only `tool.truth.view` appears in freecam entitlement gate).
- `RISK`: `camera.set_mode` metadata does not encode mode-specific capability/entitlement policy; enforcement is split between command registry and ad-hoc runtime logic.

## Axis F - Command Graph vs UI
Status: `partially_enforced`

- `INFO`: UI binding table maps to canonical command keys (`libs/appcore/ui_bind/ui_command_binding_table.c`).
- `INFO`: RepoX enforces canonical binding existence (`check_ui_canonical_command_bindings`).
- `RISK`: Parity checks are mostly static parsing checks and do not execute full CLI/TUI/GUI semantic equivalence for each bound command path.

## Axis G - Epistemics vs Rendering
Status: `partially_enforced`

- `INFO`: Freecam observer mode entitlement refusal exists in runtime (`client/shell/client_shell.c` checks `tool.truth.view`, emits `CAMERA_REFUSE_ENTITLEMENT`).
- `RISK`: RepoX renderer truth check blocks only three hardcoded tokens (`authoritative_world_state`, `truth_snapshot_stream`, `hidden_truth_cache`) and can miss semantically equivalent truth access patterns.
- `RISK`: Test assertions for freecam refusal taxonomy use broad refusal code (`WD-REFUSAL-SCHEMA`) while docs specify camera-specific refusal detail taxonomy; this weakens regression precision.

## Axis H - Collapse / Expand Consistency
Status: `partially_enforced`

- `INFO`: Collapse/expand APIs and tests exist across engine/game/test surfaces.
- `INFO`: Solver registry schema and contract tests validate structure (`data/registries/solver_registry.json`, `tests/ops/universe_complexity_contract_tests.py`).
- `RISK`: Solver registry usage appears contract-only; no direct runtime call sites found for `core_solver_select` or registry consumption in engine/game runtime.

## Axis I - Security / Cheating Claims
Status: `partially_enforced`

- `INFO`: Entitlement gate exists for observer freecam in client shell.
- `RISK`: RepoX security checks are token presence checks, not control-flow proofs; bypass risk remains if equivalent logic is introduced with different symbols.
- `RISK`: Docs claim broad anti-cheat guarantees while enforcement demonstrates partial structural coverage; claim/evidence gap remains.

## Axis J - Terminology and Duplication
Status: `partially_enforced`

- `VIOLATION`: Mixed governance vocabulary still exists in derived docs:
  - Capability-only canon is canonical.
  - Stage-centric derived docs still define runtime semantics.
- `RISK`: Duplicate security docs with overlapping normative statements increase drift risk.

## Axis K - Dead / Unreachable Code
Status: `partially_enforced`

- `RISK`: Several capability IDs are declared but currently unused in runtime checks (dead policy surface).
- `RISK`: Solver contract surfaces exist without proven runtime integration (potentially dormant architecture path).
- `INFO`: No obvious dead-gate failures in current CI; all target suites pass.

## Axis L - Future Risk Surfaces
Status: `partially_enforced`

- `RISK`: Token-based RepoX checks are brittle against symbol renaming and non-literal bypasses.
- `RISK`: Static matrix tests do not provide full behavioral proof for capability gating under real runtime execution.
- `RISK`: Overlapping capability providers without strict conflict-fail policy can cause future nondeterministic pack resolution behavior.

## Required Classification Summary
- `ENFORCED`: entry gates, strict builds, core schema versioning shape checks, canonical command/UI binding presence.
- `PARTIALLY ENFORCED`: process-only mutation, anti-cheat proofs, capability enforcement completeness, collapse/expand runtime solver wiring.
- `UNENFORCED`: none detected as fully absent; gaps are mostly partial/semantic depth.
- `CONTRADICTED`: capability-only canonical policy vs stage-centric derived runtime docs.
