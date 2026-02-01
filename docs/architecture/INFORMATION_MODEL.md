Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Information Model (INFO0)

Status: binding.  
Scope: symbolic information flow, computation, and communication constraints.

## Core invariant
**Information is symbolic state carried by signals, processed by computation,
constrained by bandwidth, latency, energy, heat, law, and trust.**

Information is not:
- free
- instantaneous
- globally visible
- perfectly reliable

## Primitives (authoritative)
Information is represented through four data primitives:
- **Signal data** (`schema/signal.data.schema`)
- **Network nodes** (`schema/network.node.schema`)
- **Network links** (`schema/network.link.schema`)
- **Capacity profiles** (`schema/network.capacity.schema`)

All numeric values are fixed-point in authoritative logic and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## Process-only mutation
Information state changes only via Process execution. Canonical process
families (data-defined) include:
- `org.dominium.process.signal.send`
- `org.dominium.process.signal.route`
- `org.dominium.process.signal.receive`
- `org.dominium.process.signal.store`
- `org.dominium.process.signal.drop`

No per-tick packet stepping, socket simulation, or wall-clock timing is allowed.

## Capacity, latency, and uncertainty
- Bandwidth and latency are symbolic, bounded, and deterministic.
- Error rates and congestion policies are explicit.
- Uncertainty is propagated; misinformation is represented by increased
  uncertainty and corruption flags, never by hidden state.

## Computation and storage
- Compute nodes have bounded capacity per tick.
- Storage nodes have bounded capacity and explicit failure modes.
- Computation consumes energy (T11) and produces heat (T12); these costs are
  declared and auditable, never implicit.

## Networks & resolution
- Resolution is event-driven, interest/budget bounded, and deterministic.
- Routing is graph-based and ordered; no global scans or adaptive heuristics.
- Reliability is enforced via deterministic ordering and fixed-point math.

## Collapse/expand compatibility
Macro capsules store:
- total data stored per domain (invariant)
- traffic distributions and error-rate histograms (sufficient statistics)
- RNG cursor continuity for error/corruption streams

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Law & refusal semantics
All information emission and routing is law/meta-law gated. Refusals must
explain the violated constraint per `docs/architecture/REFUSAL_SEMANTICS.md`.

## Non-goals (INFO0)
- No packet-level simulation.
- No real-time clocks or wall-clock dependencies.
- No continuous solvers.

## See also
- `docs/architecture/SIGNAL_MODEL.md`
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`