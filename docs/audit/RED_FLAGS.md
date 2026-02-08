Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# CA-0 Red Flags

These items should be treated as must-fix before trusting architecture claims as fully enforced.

## RF-1 (VIOLATION) - Canon contradiction in docs
- Canonical doc: `docs/architecture/CAPABILITY_ONLY_CANON.md` states capability-only gating.
- Contradicting derived docs: `docs/CAPABILITY_STAGES.md`, `docs/TESTX_STAGE_MATRIX.md` prescribe stage-based runtime rules.
- Impact: governance ambiguity and prompt drift risk.

## RF-2 (VIOLATION) - Declared capability surface not fully enforced
- Declared capability IDs in `data/capabilities/app_ui_camera_blueprint.json` include:
  - `ui.camera.mode.memory`
  - `ui.camera.mode.observer`
  - `tool.observation.stream`
  - `tool.memory.read`
- Current runtime/command graph enforcement does not consistently check these IDs.
- Impact: declared policy and runtime behavior diverge.

## RF-3 (RISK) - Anti-cheat enforcement depth is shallow
- `scripts/ci/check_repox_rules.py::check_observer_freecam_entitlement_gate` verifies token presence only.
- `scripts/ci/check_repox_rules.py::check_renderer_no_truth_access` blocks only three literal tokens.
- Impact: semantic bypasses can evade static checks.

## RF-4 (RISK) - Process enforcement has coverage blind spots
- `tests/invariant/process_only_mutation_tests.py` is token-based.
- RepoX process literal scan is limited to `engine/modules/world` and `game/rules`.
- Impact: mutation paths outside token/root coverage may be missed.

## RF-5 (RISK) - Solver/conformance framework appears contract-only
- `data/registries/solver_registry.json` is validated structurally.
- No runtime call sites found for `core_solver_select` in engine/game/application runtime.
- Impact: docs assert solver-driven behavior that is not yet mechanically proven in runtime execution.

## RF-6 (RISK) - Capability matrix tests are mostly static
- `tests/testx/capability_suite_runner.py` largely parses registry/binding data and hashes payloads.
- Limited runtime execution evidence for capability-gated behavior transitions.
- Impact: can miss behavioral regressions that preserve static shapes.
