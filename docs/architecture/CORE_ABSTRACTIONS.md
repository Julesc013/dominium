Status: DERIVED
Last Reviewed: 2026-02-28
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: ABS-1 universal deterministic abstraction substrate for graph/flow/constraints/state/hazard/schedule/spatial.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Core Abstractions

## Purpose
Prevent subsystem drift by standardizing reusable deterministic substrates for graph-like, flow-like, schedule-like, and state-machine-like systems while preserving existing simulation semantics.

## A) NetworkGraph
- `NetworkGraph` is the universal node/edge substrate reused by logistics, interiors (volumes/portals), mobility networks, power, water, signal networks, and future delegation graphs.
- Node and edge payload typing is indirect through schema references (`node_type_schema_id`, `edge_type_schema_id`) and payload objects.
- Traversal/routing must be deterministic:
  - stable ordering by ID
  - deterministic tie-breaks (`edge_id` lexical baseline)
  - deterministic multi-hop policy selection
- ID policy:
  - graph, node, and edge IDs are explicit stable IDs
  - no implicit/generated runtime IDs for canonical graph topology

## B) FlowSystem
- `FlowChannel` is the universal flow declaration over `NetworkGraph` for materials, energy, fluids/pressure, signals/data, and future ledger-typed flow channels.
- Solver interface is tiered:
  - coarse deterministic solver is baseline
  - richer solvers may be added by policy without changing contracts
- Flow quantities must be tied to `quantity_id` and integrate with RS-2 ledger accounting.
- Flow never mutates truth directly outside process commit boundaries.

## C) ConstraintComponent
- `ConstraintComponent` attaches deterministic constraints to assemblies/nodes/participants.
- Standard baseline constraint families:
  - guide constraints
  - docking constraints
  - coupling constraints
  - sealing constraints
- Enforcement is policy-driven with deterministic participant ordering.
- Constraints are declarative and do not imply immediate physics solver execution.

## D) StateMachineComponent
- `StateMachineComponent` standardizes deterministic process-triggered transitions.
- Used for doors, signals, machine operational states, project states, and similar toggles.
- Transitions are process-triggered only (no UI/runtime direct mutation).
- Conflict resolution:
  - priority order first
  - stable lexical transition ID tie-break

## E) HazardModel
- `HazardModel` standardizes hazard accumulation and threshold consequence triggering.
- Supports macro-first operation with optional micro refinement in ROI.
- Default trigger mode is deterministic threshold crossing.
- Named RNG stochastic triggering is allowed only via explicit policy and named streams.

## F) ScheduleComponent
- `ScheduleComponent` is the unified deterministic scheduling substrate for:
  - construction steps
  - logistics manifests
  - maintenance cycles
  - future timetables/recurrence
- Recurrence and cancellation are explicit policy/data contracts.
- Next-due computation is deterministic from schedule state and simulation tick.

## G) SpatialNode Hierarchy
- `SpatialNode` unifies nested spatial reference frames:
  - galaxy -> system -> body -> region -> site -> interior volume
- Transform composition and parent-chain traversal are deterministic.
- Parent chains must remain acyclic.
- Rendering does not own these transforms; this is simulation-side spatial structure.

## H) Capability Tags
- Capability tags are lightweight standardized labels for query/discovery.
- Tags are for data lookup and composition, not hidden behavior mode switches.
- Behavior remains driven by processes, law profile, authority context, and explicit policies.

## Migration Requirements
- Existing subsystems must reuse this substrate instead of re-implementing local graph/flow/schedule/state stacks.
- MAT-4 logistics migration requirement:
  - logistics graph internals map to `NetworkGraph`
  - shipment transfer semantics map to `FlowSystem`
  - external manifest behavior/refusals remain unchanged
- Compatibility shims are allowed as temporary adapters, with explicit deletion path.

## Non-Duplication Rule
- New independent graph engines outside `src/core/graph` are forbidden.
- New independent schedulers outside `src/core/schedule` are forbidden.
- Ad-hoc state machine engines outside `src/core/state` are forbidden.
- Quantity flow paths must use core flow substrate plus ledger accounting or explicit exception declaration.

## Extension Pattern
1. Define payload schema for node/edge/flow-specific metadata.
2. Register deterministic routing/solver/schedule policies in registries.
3. Execute mutations through process pipeline only.
4. Preserve deterministic ordering and refusal semantics.
5. Add RepoX/AuditX/TestX guardrails before enabling gameplay-facing behaviors.
