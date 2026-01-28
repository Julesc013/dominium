# SPEC_LAW_KERNEL (EXEC0c)

Schema ID: LAW_KERNEL
Schema Version: 1.0.0
Status: binding.
Scope: canonical law kernel interface and evaluation contract.
Non-goals: runtime implementation.

## Purpose
Define the deterministic law kernel that gates commands, tasks, commits, and
information emission across all execution backends.

## Law Types
- Existence Law (meta-law): may this mechanic exist or operate here at all?
- Capability Law: may this actor/session/tool attempt or observe?
- Policy Law: constraints on allowed actions (limits, consent, rate caps).

Evaluation order is fixed and deterministic:
1) Existence law
2) Capability law
3) Policy law

## Law Kernel Interface
The law kernel evaluates a declared context and targets to produce a decision.

Inputs:
- LawEvaluationContext (see below)
- law_targets (see SPEC_LAW_TARGETS)

Output:
- LawDecision (see SPEC_LAW_EFFECTS)

## Law Evaluation Context (Declared Inputs Only)
The context contains only declared inputs and must be deterministic:
- scope_chain (see SPEC_LAW_SCOPES)
- actor_ref (optional)
- organization_ref (optional)
- jurisdiction_ref (optional)
- capability_set_ref (optional)
- action_or_task_targets (law_targets list)
- time_act (ACT tick)
- determinism_class
- fidelity_tier
- cost_model (upper bounds only)
- policy_params (deterministic parameters)

Forbidden:
- hidden reads of authoritative world state
- wall-clock time
- randomness

## Capability Law: Additive and Subtractive
Capability law supports:
- grants (additive)
- denies (negative capabilities)
- parameterized capabilities

Negative capabilities take precedence unless explicitly overridden by a higher
scope in the scope chain.

## Lifecycle States (Preview)
Law sources may be in one of:
- active
- scheduled (future)
- deprecated
- retired

Transitions affecting existing state MUST declare one of:
- grandfather
- migrate
- quarantine
- destroy (only if explicitly permitted and auditable)

## Auditability and Explainability
Every REFUSE, TRANSFORM, or CONSTRAIN decision MUST emit:
- refusal code (if REFUSE)
- violated law references
- precedence chain explanation
- epistemic visibility classification

All decisions must be deterministic and auditable.

## Cross-References
- Scopes: `schema/law/SPEC_LAW_SCOPES.md`
- Targets: `schema/law/SPEC_LAW_TARGETS.md`
- Effects: `schema/law/SPEC_LAW_EFFECTS.md`
- Enforcement points: `docs/architecture/LAW_ENFORCEMENT_POINTS.md`
