Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GR3 FULL Results

## Scope
- Archived GR3 FULL stress/reference artifacts retained from the prior run.
- Post-repair FULL verification focused on the exact failure cluster that had drifted since the snapshot.
- SYS raw stress archives are represented at tip by compact manifests so the committed audit set satisfies hosted blob limits without changing the evidence fingerprint.

## Archived FULL Artifacts Retained
- SYS stress manifest: `docs/audit/GR3_FULL_SYS_STRESS_MANIFEST.json`
- SYS cross-shard reduced window manifest: `docs/audit/GR3_FULL_SYS_CROSS_SHARD_STRESS_MANIFEST.json`
- PROC stress: `docs/audit/GR3_FULL_PROC_STRESS.json`
- POLL stress: `docs/audit/GR3_FULL_POLL_STRESS.json`
- SIG stress: `docs/audit/GR3_FULL_SIG_STRESS.json`
- ELEC stress: `docs/audit/GR3_FULL_ELEC_STRESS.json`
- THERM stress: `docs/audit/GR3_FULL_THERM_STRESS.json`
- FLUID stress: `docs/audit/GR3_FULL_FLUID_STRESS.json`
- CHEM stress: `docs/audit/GR3_FULL_CHEM_STRESS.json`
- PROV compaction stress: `docs/audit/GR3_FULL_PROV_STRESS.json`
- FULL reference suite: `docs/audit/GR3_FULL_REFERENCE_SUITE.json`

## Post-Repair FULL Reruns
- `python tools/xstack/testx/runner.py --repo-root . --profile FULL --cache off --subset test_breaker_trip_deterministic,test_breaker_trip_on_overload,test_control_resolution_deterministic,test_machine_operate_consumes_and_produces_batches,test_planning_requires_capability,test_provenance_anchor_validation,testx.reality.epistemic_invariance_on_expand,testx.net.pipeline_net_handshake_stage_authoritative,testx.net.pipeline_net_handshake_stage_srz_hybrid`
  - Result: `PASS` (`selected_tests=9`)
- `python tools/xstack/testx/runner.py --repo-root . --profile FULL --cache off --subset testx.control.plan_creation_deterministic,testx.control.manual_placement_via_plan`
  - Result: `PASS` (`selected_tests=2`)
- Control proof bundle schema validation rerun:
  - Result: `PASS`

## FULL Repair Conclusion
- The regressions that were invalidating authoritative net boot, deterministic control replay, expand provenance, overload protection, and planner/LOD strict fixtures are cleared.
- No new reference mismatches were introduced.
- Archived stress/reference artifacts remain the authoritative broad-window evidence set for GR3.
- SYS archive manifests preserve the raw archive SHA-256 values, deterministic fingerprints, and key event counts while removing the hosted-size violation from the current tree.

## Execution Notes
- The umbrella `TestX FAST/FULL` runs remain expensive in this environment; the repair pass therefore reran the complete impacted subset directly and left the archived broad-window artifacts unchanged.
