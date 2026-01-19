# SPEC_WORK_IR (EXEC0)

Status: binding.
Scope: canonical Work IR (Task Graph) representation.
Non-goals: scheduler implementation, ECS integration, or runtime code.

## Purpose
Work IR defines a stable, declarative, deterministic representation of
computation so gameplay systems describe what must be done while execution
backends decide how and where it runs.

## Core Types

### TaskGraph
Represents a single immutable graph of work.

Fields:
- graph_id: stable, deterministic identifier for this graph instance.
- epoch_id: sim-affecting version boundary (ties to compatibility epoch).
- tasks: ordered set of TaskNode entries.
- dependencies: ordered list of DependencyEdge entries.
- phase_boundaries: ordered list of PhaseBoundary entries (explicit barriers).

Rules:
- A TaskGraph is immutable after emission.
- tasks MUST be emitted in deterministic order. Canonical order is ascending
  task_id unless a spec defines a different stable order.
- dependencies MUST be acyclic.
- phase boundaries MUST be explicit; no implicit global barriers.

### TaskNode
Represents a single unit of computation.

Fields:
- task_id: stable, deterministic identifier for the task.
- system_id: originating system identifier (stable token).
- category: AUTHORITATIVE | DERIVED | PRESENTATION
- determinism_class: STRICT | ORDERED | COMMUTATIVE | DERIVED
- access_set_ref: reference to an AccessSet (see SPEC_ACCESS_IR).
- cost_model_ref: reference to a CostModel (see SPEC_COST_MODEL).
- law_targets: ordered list of mechanic class identifiers (e.g., WAR, ECONOMY).
- law_scope_ref: reference to law scope (see schema/law/SPEC_LAW_SCOPES.md).
- actor_ref: optional actor identifier.
- capability_set_ref: optional capability set identifier.
- policy_params: deterministic parameters for law evaluation.
- next_due_tick: optional ACT tick for scheduled execution.
- fidelity_tier: latent | macro | meso | micro | focus

Rules:
- TaskNode is side-effect free outside declared writes.
- TaskNode is deterministic given identical inputs.
- TaskNode MUST NOT mutate state without declared writes.
- TaskNode MUST NOT read state without declared reads.
- TaskNode MUST declare law_targets (non-empty for AUTHORITATIVE tasks).
- TaskNode MUST declare law_scope_ref.
- TaskNode MUST reference an AccessSet and CostModel.
- TaskNode determinism_class is immutable at runtime.

### DependencyEdge
Represents an ordering requirement between tasks.

Fields:
- from_task_id: upstream task (must complete first).
- to_task_id: downstream task (may start after).
- reason: optional stable token for audit/explanation.

Rules:
- Dependencies must be explicit; hidden ordering is forbidden.

### PhaseBoundary
Represents a barrier between explicit phases.

Fields:
- phase_id: stable identifier for the phase.
- before_tasks: ordered set of task_id values that must complete.
- after_tasks: ordered set of task_id values that must not start earlier.

Rules:
- Phases are declarative barriers. Use only when dependencies are insufficient.

## Law Integration (Binding)
Before scheduling any TaskNode:
1. Existence law is evaluated.
2. Capability law is evaluated.
3. Policy law is applied.

Possible outcomes:
- ACCEPT
- REFUSE (with deterministic explanation)
- TRANSFORM (e.g., lower fidelity tier or delayed next_due_tick)

Law evaluation MUST be deterministic and auditable.
Law gate enforcement points are defined in
`docs/arch/LAW_ENFORCEMENT_POINTS.md`.

## Determinism and Ordering
- TaskGraph output MUST be deterministic under identical inputs.
- Order-sensitive tasks MUST declare determinism_class STRICT or ORDERED.
- Reordering is allowed only when determinism_class permits it.

## Degradation and Absence
- Tasks may be degraded by lowering fidelity_tier, increasing next_due_tick
  spacing, or collapsing into aggregate tasks.
- Entire systems may be absent. Absence MUST NOT break simulation correctness.

## Counterfactual Rule
Work IR is authoritative only. Counterfactual work MUST:
- run in shadow instances,
- be marked DERIVED,
- never commit effects to authoritative state.

## Forbidden Patterns
- Hidden global scans.
- Execution policy encoded in gameplay code.
- Undeclared access behind pointers or callbacks.
- Determinism class changes at runtime.
