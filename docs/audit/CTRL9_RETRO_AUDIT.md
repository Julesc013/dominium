Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: CTRL-9 retro-consistency audit for control plane completeness
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CTRL9 Retro Audit

## Canon/Invariant Frame
- `docs/canon/constitution_v1.md` A1, A2, A3, A4, A7, A10.
- `docs/canon/glossary_v1.md` (AuthorityContext, Capability, Determinism, Refusal).
- `AGENTS.md` process-only mutation, no runtime mode flags, deterministic ordering.
- Target CTRL-9 invariants:
  - `INV-CONTROL-PLANE-ONLY-DISPATCH`
  - `INV-CONTROL-INTENT-REQUIRED`
  - `INV-NO-DOMAIN-DOWNGRADE-LOGIC`
  - `INV-VIEW-CHANGES-THROUGH-CONTROL`
  - `INV-NO-ADHOC-TEMP-MODIFIERS`
  - `INV-NO-TYPE-BRANCHING`

## Audit Method
- Intent/envelope construction scan:
  - `rg -n "build_client_intent_envelope\(|_build_envelope\(" src tools -g "*.py"`
- Domain downgrade scan:
  - `rg -n "downgrade\.|build_downgrade_entry\(" src -g "*.py"`
- View/camera mutation scan:
  - `Select-String -Pattern 'state\["camera_assemblies"\]\s*=|state\["view_bindings"\]\s*=' src,tools/**/*.py`
- Temporary modifier scan:
  - `Select-String -Pattern 'interior_movement_constraints|temporary_|temp_|\*=\s*0\.[0-9]+' src,tools/xstack/sessionx/**/*.py`
- Type-branching scan in control subsystem:
  - `Select-String -Pattern 'entity_type|assembly_type|entity_class|assembly_class|target_kind\s*==' src/control/**/*.py`

## Findings

### F1 - Direct intent envelope creation remains outside `src/control` in network policy adapters
- Paths:
  - `src/net/policies/policy_server_authoritative.py`
  - `src/net/srz/shard_coordinator.py`
- Assessment:
  - No public interaction bypass detected; these are transport/network adapter entrypoints.
  - Interaction entry (`src/client/interaction/interaction_dispatch.py`) still routes through `build_control_intent` and `build_control_resolution` before process execution.
- Action:
  - Keep as allowed adapter paths under `INV-CONTROL-PLANE-ONLY-DISPATCH`.
  - Harden RepoX with `INV-CONTROL-INTENT-REQUIRED` for public-facing interaction entrypoints.

### F2 - Inline downgrade logic in domain modules
- Result: none detected outside control subsystem.
- Notes:
  - Downgrade logic remains in control subsystem (`src/control/negotiation/*`, `src/control/view/*`, `src/control/fidelity/*`) as intended.

### F3 - Direct camera/view mutation outside control/view engine
- Result: none detected outside process runtime.
- Notes:
  - `state["camera_assemblies"]` and `state["view_bindings"]` writes found only in `tools/xstack/sessionx/process_runtime.py`.

### F4 - Temporary modifiers outside effect system
- Result: none detected in runtime scans.
- Notes:
  - No remaining `interior_movement_constraints` / `temporary_*` runtime flags in `src/` or `tools/xstack/sessionx/`.

### F5 - Type branching in control resolution paths
- Result: no entity-type/class branching detected in control resolution.
- Notes:
  - `process_id == ...` checks remain in `src/control/ir/control_ir_compiler.py` for deterministic IR mapping; this is process routing, not gameplay type branching.

## Remaining Violations
- No hard violations detected in runtime interaction/control paths from this audit pass.
- Residual risk area: future domain modules introducing public interaction entrypoints without ControlIntent creation.

## Required Deprecation Entries
- None required from current findings.
- Existing adapter/deprecation governance remains sufficient for this phase.

## Migration/Hardening Plan
1. Promote control-plane and mode/type/temporary-modifier invariants to hard-fail behavior in FAST checks.
2. Add `INV-CONTROL-INTENT-REQUIRED` for public-facing interaction entrypoints.
3. Expand topology/semantic-impact contracts so control-plane edits trigger deterministic regression suites.
4. Add control decision-log baseline lock and enforce update-tag gating.
5. Add stress and multiplayer fairness regression tests to prevent refactor drift.
