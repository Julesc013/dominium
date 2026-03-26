Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f32da9045a183d79`

- Symbol: `_semantic_geo_cell_key`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/worldgen/refinement/refinement_cache.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/worldgen/refinement/refinement_cache.py`
- `src/worldgen/refinement/refinement_scheduler.py`

## Scorecard

- `src/worldgen/refinement/refinement_cache.py` disposition=`canonical` rank=`1` total_score=`65.0` risk=`HIGH`
- `src/worldgen/refinement/refinement_scheduler.py` disposition=`quarantine` rank=`2` total_score=`62.38` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/ARCH_AUDIT_FIX_PLAN.md, docs/audit/GEO_IDENTITY_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MW0_RETRO_AUDIT.md, docs/audit/MW3_RETRO_AUDIT.md, docs/audit/MW4_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/WORLDGEN_LOCK0_RETRO_AUDIT.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
