Status: DERIVED
Last Reviewed: 2026-02-28
Scope: CTRL-0 Phase 0 retro-consistency audit

# CTRL0 Retro-Consistency Audit

## Canon Inputs
- docs/canon/constitution_v1.md
- docs/canon/glossary_v1.md
- docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md
- docs/architecture/BOUNDARY_ENFORCEMENT.md

## Audit Summary
This audit focused on distributed control paths prior to CTRL runtime implementation. Findings are migration targets only; no runtime behavior changes are introduced in CTRL-0.

## Findings

### F1 — Direct intent envelope + execution from interaction dispatch
- Audit Item: direct IntentEnvelope creation outside net ingress/tests; duplicate control dispatch
- Paths:
  - src/client/interaction/interaction_dispatch.py
- Subsystem: client interaction dispatch
- Evidence:
  - `build_interaction_envelope(...)` constructs envelope payloads.
  - `execute_affordance(...)` imports and calls `execute_intent(...)` directly.
- Risk:
  - Bypasses a unified control gateway.
  - Keeps control decisions split between interaction and runtime process dispatch.
- Proposed migration:
  - Route interaction execution through `src/control/control_plane_engine.*`.
  - Keep interaction module limited to ControlIntent creation + UI feedback.
- Deprecation entry needed:
  - `deprecated_id`: `src/client/interaction/interaction_dispatch.py#build_interaction_envelope`

### F2 — Generic envelope builder outside net ingress
- Audit Item: direct IntentEnvelope creation outside net ingress/tests
- Paths:
  - tools/xstack/sessionx/srz.py
- Subsystem: sessionx SRZ helpers
- Evidence:
  - `build_intent_envelopes(...)` builds envelope structures in shared tooling module.
- Risk:
  - Broad helper availability increases bypass surface before control-plane centralization.
- Proposed migration:
  - Keep net ingress builders canonical.
  - Move non-test envelope build paths behind control-plane APIs.
- Deprecation entry needed:
  - `deprecated_id`: `tools/xstack/sessionx/srz.py#build_intent_envelopes`

### F3 — Ad-hoc freecam/occlusion bypass path
- Audit Item: ad-hoc camera/freecam control outside view policy
- Paths:
  - tools/xstack/sessionx/observation.py
- Subsystem: observation/perception
- Evidence:
  - `_interior_occlusion_bypass_allowed(...)` checks `lens.nondiegetic.freecam` and law epistemic limit flags directly.
- Risk:
  - View/occlusion policy logic is partially embedded in observation code instead of a dedicated control/view policy resolver.
- Proposed migration:
  - Move bypass resolution decisions into `ViewPolicy` evaluation in control plane.
  - Observation consumes resolved policy outcomes only.
- Deprecation entry needed:
  - `deprecated_id`: `tools/xstack/sessionx/observation.py#_interior_occlusion_bypass_allowed`

### F4 — Window action dispatch acts as parallel control path
- Audit Item: duplicate control-like systems
- Paths:
  - tools/xstack/sessionx/ui_host.py
- Subsystem: sessionx UI host tooling
- Evidence:
  - `build_intent_from_action(...)` builds process intents.
  - `dispatch_window_action(...)` executes intent via `execute_single_intent_srz(...)`.
- Risk:
  - Parallel command pathway outside a single control-plane gateway.
- Proposed migration:
  - UI host should emit ControlIntents and invoke control-plane resolution API.
- Deprecation entry needed:
  - `deprecated_id`: `tools/xstack/sessionx/ui_host.py#dispatch_window_action`

### F5 — Control CLI executes processes without control plane mediation
- Audit Item: duplicate control-like systems; direct tool mutation path
- Paths:
  - tools/control/control_cli.py
- Subsystem: control CLI tooling
- Evidence:
  - `_intent_for_command(...)` and `_execute_command(...)` synthesize intents and execute via scheduler.
  - Writes resulting state with `write_canonical_json(...)`.
- Risk:
  - Tool-level authoritative command path remains separate from future control-plane policy/degradation/proof logging.
- Proposed migration:
  - CLI should submit ControlIntents to control plane and persist returned committed state/proofs.
- Deprecation entry needed:
  - `deprecated_id`: `tools/control/control_cli.py#_execute_command`

### F6 — CIV admin overrides do not emit explicit meta-law exception entries
- Audit Item: admin overrides that are silent
- Paths:
  - tools/xstack/sessionx/process_runtime.py
- Subsystem: civ process runtime
- Evidence:
  - `_civ_admin_override(...)` gates ownership checks in CIV mutation paths (e.g., affiliation/order cancel).
  - Unlike `process.camera_teleport` and `process.meta_pose_override`, these override paths do not emit `exception.meta_law_override` ledger entries.
- Risk:
  - Override is lawful but not consistently forensic for meta-law usage.
- Proposed migration:
  - In CTRL migration, require AL4 meta intents for CIV admin override and emit explicit exception + proof entries.
- Deprecation entry needed:
  - `deprecated_id`: `tools/xstack/sessionx/process_runtime.py#_civ_admin_override`

### F7 — Multiple control-like dispatch gateways in repository
- Audit Item: duplicate control-like systems
- Paths:
  - src/client/interaction/interaction_dispatch.py
  - tools/xstack/sessionx/ui_host.py
  - tools/control/control_cli.py
  - tools/xstack/sessionx/scheduler.py
- Subsystem: cross-cutting control/interaction/tooling
- Evidence:
  - Intent construction and process dispatch responsibilities are spread across client, tool host, CLI, and session scheduler helpers.
- Risk:
  - Policy drift, uneven downgrade behavior, and proof logging inconsistency.
- Proposed migration:
  - Consolidate gateways under `src/control/*`; enforce gateway-only routing.
- Deprecation entry needed:
  - module-level deprecations for pre-control-plane dispatch entrypoints listed above.

## Non-Findings

### N1 — Hardcoded runtime mode flags
- Audit Item: mode flag usage
- Result: no direct `debug_mode`/`godmode` runtime branches were identified in current scanned control paths.
- Note:
  - Existing behavior remains policy/entitlement-driven, but freecam and view handling are still distributed (see F3/F7).

### N2 — Planning ghost mutating truth directly
- Audit Item: planning/blueprint execution mutating truth
- Result: no direct planning mutation path identified in preview generation.
- Path reviewed:
  - src/client/interaction/preview_generator.py
- Note:
  - Planning/execution separation still needs control-plane mediation for all execute paths.

## Migration Priorities for CTRL-1
1. Introduce control-plane gateway and route interaction/CLI/UI-host dispatch through it.
2. Replace ad-hoc view/freecam bypass checks with ViewPolicy decisions.
3. Convert CIV admin override to explicit AL4 meta intent flow with ledger exception + proof log.
4. Tighten whitelist/blockers after control-plane migration is in place.
