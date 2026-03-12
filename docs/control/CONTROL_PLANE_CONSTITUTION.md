Status: CANONICAL
Last Reviewed: 2026-02-28
Scope: CTRL-0 constitutional baseline
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Control Plane Constitution

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define a single deterministic gateway from user/AI/admin requests to authoritative processes without mode flags or hidden bypass paths.

## A) Control Planes and Roles
- `ControlIntent`
  - The normalized request submitted by player, AI, admin, automation, or replay controls.
  - Contains requested abstraction/fidelity/view/epistemic vector and requested operation.
- `Control IR`
  - Optional deterministic intermediate program for multi-step control.
  - Must be schema-validated, bounded, and deterministic.
- `ControlPolicy`
  - Resolves whether request is accepted, transformed, degraded, or refused under law/authority/server constraints.
- `PlanningPolicy`
  - Governs planning-only behavior, plan-to-commit separation, ghost artifact limits, and execution promotion gates.
- `FidelityPolicy`
  - Negotiates solver/materialization fidelity (`micro|meso|macro`) under law and budget envelopes.
- `ViewPolicy`
  - Governs camera/view requests and transition rules.
- `EpistemicPolicy`
  - Governs observable precision/scope disclosure and redaction.
- `BudgetPolicy`
  - Applies RS-5 cost envelope arbitration and deterministic degradation.
- `ProofLog`
  - Deterministic record of control decisions, degradations, refusals, overrides, and produced intents/commitments.

## B) Abstraction Levels (AL0–AL4)
- `AL0` Direct embodied micro control (diegetic).
- `AL1` Assisted/autopilot local control.
- `AL2` Scheduled/commitment-based meso control.
- `AL3` Planning/ghost + blueprint compilation (derived-only).
- `AL4` Administrative meta-law override (explicitly logged and governable).

Rules:
- Caller can request any AL; policy may downgrade or refuse.
- No runtime mode branches are permitted.

## C) Negotiation Axes
Control negotiation uses a deterministic vector:
- `abstraction_level_requested`
- `fidelity_requested` (`micro|meso|macro`)
- `view_requested` (`first|third|free|spectator|admin|replay`)
- `epistemic_scope_requested`
- `budget_requested` (inspection/reenactment etc.)
- `policy_context`:
  - `LawProfile`
  - `AuthorityContext`
  - `ServerProfile`
  - `UniversePhysicsProfile`
  - active control/view/fidelity/planning/budget policy IDs

## D) Deterministic Degradation Rules
Control plane must degrade deterministically and explainably:
- Fidelity: `micro -> meso -> macro`
- Control path: `direct -> assisted -> scheduled -> refuse`
- View path: `admin/free -> spectator -> constrained follow -> refuse`

Every downgrade emits:
- downgrade reason code
- remediation hint
- proof log decision entry

No silent fallback is allowed.

## E) Planning vs Execution Separation
- `PlanIntent`
  - Produces derived artifacts only (ghosts, BOM/AG plans, route projections, reenactment previews).
  - Must not mutate canonical truth.
- `ExecuteIntent`
  - May create commitments/intents/process envelopes.
  - Truth mutation only occurs through process execution and commit-phase rules.
- MAT-8 rule remains binding:
  - No execution without required commitments/events under configured strictness.

## F) Meta-law Override Rules
- Meta overrides are explicit `ControlIntent` requests at `AL4`.
- Required outputs for each accepted override:
  - RS-2 ledger exception entry (`exception.meta_law_override` or equivalent contract-approved type)
  - MAT provenance event(s)
  - control proof log entry
- Ranked servers reject `AL4` meta overrides.

## G) Replay/Reenactment Rules
- Replay/reenactment sessions are derived-only views.
- Allowed replay controls:
  - view/camera navigation
  - fidelity requests
  - reenactment generation requests
- Replay control must not mutate canonical truth.
- Any replay mutation request is refused deterministically.

## H) Enforcement
- Direct IntentEnvelope construction/dispatch outside control gateway is forbidden (except net ingress + approved tests during migration).
- No hidden privilege paths.
- Control plane is the only gateway from interaction/tool/control clients to process execution.
- Differences in behavior must derive from profile/policy data, not mode flags.

## Contract Dependencies
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/BOUNDARY_ENFORCEMENT.md`
- `docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`
- `docs/contracts/refusal_contract.md`
