Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.6d412b76b6fdff3e`

- Symbol: `_hash_chain`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/fluid/tool_run_fluid_stress.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/fluid/tool_run_fluid_stress.py`
- `tools/geo/geo10_stress_runtime.py`

## Scorecard

- `tools/fluid/tool_run_fluid_stress.py` disposition=`canonical` rank=`1` total_score=`71.36` risk=`HIGH`
- `tools/geo/geo10_stress_runtime.py` disposition=`quarantine` rank=`2` total_score=`64.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/CHEM_DEGRADATION_BASELINE.md, docs/audit/DOC_INDEX.md, docs/audit/FLUID3_RETRO_AUDIT.md, docs/audit/FLUID_CONTAINMENT_BASELINE.md, docs/audit/FLUID_FINAL_BASELINE.md, docs/audit/GEO_GEOMETRY_EDIT_BASELINE.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
