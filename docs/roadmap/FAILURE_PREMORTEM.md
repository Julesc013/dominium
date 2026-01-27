# Failure Pre-Mortem (ROADMAP)

Status: planning.
Scope: awareness only; no solutions.

## Where shortcuts are most tempting
- Bypassing law or capability gates for convenience.
- Hardcoding defaults instead of honoring data contracts.
- Skipping provenance or audit to save time.
- Using nondeterministic APIs in authoritative paths.

## Systems most likely to be overloaded
- Law kernel and authority resolution.
- Work IR scheduling and Access IR enforcement.
- Refinement lattice and worldgen budgets.
- Epistemic artifact pipelines and knowledge gating.

## Where performance regressions may appear
- Unbounded refinement requests or global scans.
- Per-ACT iteration outside scheduled events.
- Excessive audit or provenance writes.
- Cross-domain travel and sharding boundaries.

## Distributed determinism failure modes to watch
- Treating distribution as "different rules" instead of projection.
- Allowing double-owned domains during shard handoff.
- Cross-shard messages mutating state outside admission control.
- Wall-clock coupling leaking into authoritative ordering.

## Concepts hardest for new contributors
- Determinism rules and enforcement gates.
- Law, policy, capability, authority separation.
- Objective vs subjective reality and epistemics.
- Process, action, event, and effect lifecycle.
