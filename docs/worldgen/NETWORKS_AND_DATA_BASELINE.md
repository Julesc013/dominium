# Networks and Data Baseline (INFO0)

Status: binding for T14 baseline.  
Scope: symbolic information flow, computation, and storage without packet simulation.

## What networks are in T14
- Symbolic data movement through explicit nodes and links.
- Bandwidth and latency are bounded, deterministic, and inspectable.
- Congestion and error rates can drop or corrupt data.

All values are fixed-point and unit-tagged per
`docs/architecture/UNIT_SYSTEM_POLICY.md`.

## What exists
**Signal data**
- Discrete data items with size and uncertainty.
- Provenance and protocol references are data-defined.

**Network nodes**
- Routers, switches, antennas, satellites, compute nodes, and storage nodes.
- Bounded compute and storage capacities.
- Declared energy and heat costs per data unit.

**Network links**
- Bandwidth limits and latency classes.
- Error rates and explicit congestion policies.

**Resolution**
- Event-driven and interest-bounded.
- Deterministic ordering and fixed-point math.
- No per-tick packet stepping.

## What is NOT included yet
- No packet-level simulation or socket APIs.
- No real-time clocks or wall-clock scheduling.
- No dynamic routing optimization or adaptive heuristics.
- No trust, deception, or conflict layers beyond uncertainty flags.

## Collapse/expand compatibility
Network collapse stores:
- total data stored per domain (invariant)
- traffic distributions
- error-rate histograms

Expand reconstructs a deterministic microstate consistent with capsule stats.

## Inspection and tooling
Inspection exposes:
- node capacity and utilization
- link bandwidth and latency class
- queued, delivered, and dropped data counts
- uncertainty and corruption flags

Visualization is symbolic and never authoritative.

## Maturity labels
- Signal data: **BOUNDED** (discrete, auditable).
- Links: **BOUNDED** (explicit capacity and latency).
- Nodes: **BOUNDED** (capacity-limited, deterministic).

## See also
- `docs/architecture/INFORMATION_MODEL.md`
- `docs/architecture/SIGNAL_MODEL.md`
- `docs/architecture/ENERGY_MODEL.md`
- `docs/architecture/THERMAL_MODEL.md`
