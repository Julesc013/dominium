Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Scope: CTRL-1 baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Control Plane Engine Baseline

## Summary
CTRL-1 establishes `src/control/control_plane_engine.py` as the canonical runtime control gateway for interaction-originated actions:
- `ControlIntent` creation
- deterministic policy/vector negotiation
- `ControlResolution` emission with downgrade/refusal reasons
- deterministic decision-log artifact emission

Envelope creation is now restricted to:
- `src/control/*`
- net ingress modules
- TestX whitelisted test paths

## Schemas Integrated
- `schema/control/control_intent.schema` (`1.0.0`)
- `schema/control/control_resolution.schema` (`1.0.0`)
- `schema/control/control_policy.schema` (`1.0.0`)
- `schema/control/control_action.schema` (`1.0.0`)
- `schema/control/control_decision_log.schema` (`0.1.0`)

CompatX registry/version entries were updated to include these control schemas and registry artifacts.

## Registries Integrated
- `data/registries/control_action_registry.json`
  - includes canonical `action.*` rows for CTRL-1
  - includes legacy-compatible `control.action.*` aliases to preserve existing controller-type contracts
- `data/registries/control_policy_registry.json`
  - baseline policies:
    - `ctrl.policy.player.diegetic`
    - `ctrl.policy.player.assisted`
    - `ctrl.policy.scheduler`
    - `ctrl.policy.planner`
    - `ctrl.policy.admin.meta`
    - `ctrl.policy.replay`
- `data/registries/intent_dispatch_whitelist.json`
  - reduced to:
    - `src/net/**`
    - `src/control/**`
    - `tools/xstack/testx/tests/**`

## Runtime Integration
- Interaction flow migrated in:
  - `src/client/interaction/interaction_dispatch.py`
- Path now:
  1. Build `ControlIntent`.
  2. Resolve via `build_control_resolution(...)`.
  3. Dispatch emitted intent payload(s).
  4. Return resolution + control intent for traceability.

## Decision Logging
- Minimal deterministic decision log implemented:
  - artifact path: `run_meta/control_decisions/*.json`
  - referenced from `control_resolution.decision_log_ref`

## Enforcement Updates
- RepoX:
  - `INV-CONTROL-PLANE-ONLY-DISPATCH`
  - `INV-NO-MODE-FLAGS`
  - `INV-DECISION-LOG-REQUIRED`
- AuditX:
  - `E104_DIRECT_INTENT_BYPASS_SMELL` updated for CTRL-1 allow paths
  - `E111_INTENT_BYPASS_SMELL` updated to envelope-specific marker detection
- TestX:
  - added CTRL-1 tests:
    - `test_control_resolution_deterministic`
    - `test_control_policy_blocks_forbidden_action`
    - `test_ranked_forbids_meta_actions`
    - `test_direct_dispatch_blocked`
    - `test_decision_log_emitted`
    - `test_interaction_flow_uses_control_plane`

## Topology/Governance Updates
- `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md` regenerated.
- New control schemas/registries are now declared in topology artifact, satisfying undeclared schema/registry enforcement.

## Gate Results
- RepoX (`STRICT`): PASS
- AuditX scan: RUN (artifacts regenerated under `docs/audit/auditx/`)
- TestX (CTRL-1 targeted subset): PASS
  - `test_control_resolution_deterministic`
  - `test_control_policy_blocks_forbidden_action`
  - `test_ranked_forbids_meta_actions`
  - `test_direct_dispatch_blocked`
  - `test_decision_log_emitted`
  - `test_interaction_flow_uses_control_plane`
- strict build:
  - PASS via `cmake --build out/build/vs2026/verify --config Release`
  - required `tool_ui_bind --write` refresh before check target passed
- `ui_bind --check`: PASS

## Known Gaps for CTRL-2+
- Full Control IR program execution is not implemented in CTRL-1.
- View/fidelity arbitration hooks are currently minimal and policy-stubbed.
- Legacy tooling paths (`control_cli`, `ui_host`, task completion queue bridge) remain in deprecation/migration queue.
