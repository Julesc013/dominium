Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GR3 Performance Tuning

## Trigger
FULL run attempts exposed environment timeout hotspots on very large stress windows.

## Registry-Only Tuning Decision
No persistent registry edits were applied in GR3.

Rationale:
- Reduced deterministic windows passed assertions without requiring policy changes.
- Hotspots appear dominated by scenario scale/runtime limits in this environment, not a correctness regression requiring budget rebalance.

## Candidate Follow-Up (No Change Applied)
If long-window CI remains unstable, tune via registries only:
1. Lower non-critical coupling budgets for background owners.
2. Raise priority bias for safety-critical couplings under pressure.
3. Reduce default macro capsule evaluation frequency for distant systems.
4. Tighten compaction window cadence for derived-heavy workloads.

No code semantics changed in this phase.
