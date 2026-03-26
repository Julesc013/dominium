Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.4b99054248eccb2f`

- Symbol: `_truth_hash_anchor`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/geo/tool_replay_geo_window.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/geo/tool_replay_geo_window.py`
- `tools/xstack/testx/tests/geo10_testlib.py`

## Scorecard

- `tools/geo/tool_replay_geo_window.py` disposition=`canonical` rank=`1` total_score=`74.23` risk=`HIGH`
- `tools/xstack/testx/tests/geo10_testlib.py` disposition=`quarantine` rank=`2` total_score=`66.39` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/audit/ARCH_AUDIT0_RETRO_AUDIT.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/EARTH2_RETRO_AUDIT.md, docs/audit/EARTH3_RETRO_AUDIT.md, docs/audit/GEO10_RETRO_AUDIT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
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
