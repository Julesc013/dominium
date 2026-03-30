Status: DERIVED
Last Reviewed: 2026-03-31
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: PI
Replacement Target: snapshot-anchored executable planning map after series reprioritization

# Series Dependency Map

## Dependency Diagram

```text
XI -----> SIGMA
 | \        \
 |  \        v
 |   +-----> PHI -----> ZETA
 |            ^           ^
 v            |           |
OMEGA ------> UPSILON ----+
```

## Series Table

| Series | Purpose | Prerequisites | Outputs | Can start before snapshot mapping? | Risk |
| --- | --- | --- | --- | --- | --- |
| `Ξ` | Map repository truth, converge structural drift, eliminate forbidden source roots, freeze architecture governance, and lock repository structure. | none | architecture graph, duplicate implementation scan, source-pocket policy, architecture freeze, CI drift immunity, repository structure lock | `yes` | `high` |
| `Ω` | Lock worldgen, baseline universe, gameplay, disaster behavior, ecosystem verification, update simulation, trust, and final distribution signoff. | none | worldgen lock baseline, baseline universe baseline, gameplay loop baseline, disaster suite baseline, ecosystem verify baseline, update simulation baseline, trust strict baseline, distribution signoff | `yes` | `high` |
| `Σ` | Stabilize the unified human and Agent operating interface, including task catalogs, ControlX planning, prompt safety, and deterministic maintenance workflows. | XI, OMEGA | task catalogs, agent governance workflows, prompt safety policy, deterministic maintenance playbooks | `yes` | `medium` |
| `Φ` | Evolve the runtime toward a service-oriented kernel with lifecycle management, service registry, module loading, and replaceable component surfaces. | XI, OMEGA | lifecycle manager, service registry, module loader, componentized runtime boundaries, replaceable render and storage services | `no` | `very_high` |
| `Υ` | Turn the current release and archive foundations into a stricter control plane for package graphs, release governance, rollout policy, and operator tooling. | XI, OMEGA | release orchestration control plane, profiled CI lanes, distribution controllers, upgrade and rollback governance | `yes` | `high` |
| `Ζ` | Deliver deterministic live operations, live cutovers, distributed simulation controls, and proof-backed operational recovery. | SIGMA, PHI, UPSILON, OMEGA | shadow services, live cutover plans, deterministic replication, authority handoff, proof-backed rollback | `no` | `very_high` |

