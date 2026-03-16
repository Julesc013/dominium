Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Scope: CTRL-1 Phase 0 retro-consistency audit
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CTRL1 Retro-Consistency Audit

## Canon Inputs
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/control/CONTROL_PLANE_CONSTITUTION.md`
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`
- `docs/architecture/BOUNDARY_ENFORCEMENT.md`

## Audit Method
- Direct-dispatch and envelope scan:
  - `rg -n "build_client_intent_envelope\\(|_build_envelope\\(|execute_intent\\(" src tools -g "*.py"`
- Mode-flag scan:
  - `rg -n "debug_mode|godmode|mode_flag|freecam|free_cam|admin_mode|dev_mode" src tools docs`
- Whitelist verification:
  - `data/registries/intent_dispatch_whitelist.json`

## Findings

### F1 — Interaction execute path migrated to control plane
- Audit Item: interaction execute direct dispatch site
- Path:
  - `src/client/interaction/interaction_dispatch.py`
- Subsystem: RND/ACT interaction dispatch
- Current State:
  - `build_interaction_control_intent(...)` builds `ControlIntent`.
  - `build_control_resolution(...)` resolves policy and emits intent envelopes.
  - Dispatch executes only emitted intent rows from control resolution.
- Classification:
  - `migrate_now` complete for intent/envelope creation.
- Remaining Migration:
  - None for CTRL-1 scope.
- Deprecation Entry:
  - Existing CTRL-0 entries remain valid for legacy helpers.

### F2 — Task completion still uses runtime-local completion queue
- Audit Item: task completion dispatch site
- Paths:
  - `src/interaction/task/task_engine.py`
  - `tools/xstack/sessionx/process_runtime.py` (`process.task_tick` / pending completion intents)
- Subsystem: ACT task runtime
- Current State:
  - Completion intents are generated deterministically by task engine and consumed by process runtime queue.
  - This path is process-runtime internal and deterministic, but not yet routed through control-plane APIs.
- Classification:
  - `quarantine/deprecate` for future CTRL migration.
- Proposed Migration:
  - Route completion-intent handoff through control-plane execute bridge in CTRL-2+.
- Deprecation Entry Needed:
  - `tools/xstack/sessionx/process_runtime.py#pending_task_completion_intents`

### F3 — Tool-use non-interaction entrypoints remain legacy
- Audit Item: tool use dispatch outside control-plane gateway
- Paths:
  - `tools/control/control_cli.py`
  - `tools/xstack/sessionx/scheduler.py` (scripted intent replay path)
- Subsystem: tool/runtime orchestration
- Current State:
  - Paths can execute intents without interaction control gateway.
- Classification:
  - `quarantine/deprecate`
- Proposed Migration:
  - CLI/scheduler submit `ControlIntent` and consume `ControlResolution` artifacts.
- Deprecation Entry:
  - Existing CTRL-0 deprecation entries cover CLI/scheduler style bypasses; keep active.

### F4 — UI button path still has legacy dispatch helper
- Audit Item: UI button path direct dispatch
- Path:
  - `tools/xstack/sessionx/ui_host.py` (`dispatch_window_action`)
- Subsystem: tooling UI host
- Current State:
  - Parallel legacy dispatch path still exists in tooling domain.
- Classification:
  - `quarantine/deprecate`
- Proposed Migration:
  - UI host emits `ControlIntent` only; no direct process dispatch.
- Deprecation Entry:
  - Existing entry retained:
    - `tools/xstack/sessionx/ui_host.py#dispatch_window_action`

## Whitelist Confirmation (ARCH-REF-3)
- File: `data/registries/intent_dispatch_whitelist.json`
- Effective allowlist after CTRL-1 migration:
  - `src/net/**`
  - `src/control/**`
  - `tools/xstack/testx/tests/**`
- Result:
  - Confirmed: whitelist excludes client/tool runtime modules for envelope creation.

## Non-Findings
- No new `debug_mode` / `godmode` hard mode-flag branches detected in scanned control paths.
- No new direct TruthModel mutation paths were introduced in UI/render modules as part of CTRL-1 work.

## Migration Queue (Post-CTRL-1)
1. Move task completion queue dispatch behind control-plane execute bridge.
2. Migrate `ui_host` and `control_cli` to control-plane submit/resolve flow.
3. Keep whitelist strict: envelope creation only under `src/control/*` and net ingress.
