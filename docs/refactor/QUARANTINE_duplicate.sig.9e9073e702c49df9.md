Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9e9073e702c49df9`

- Symbol: `_quantity`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/astro/illumination/illumination_geometry_engine.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/astro/illumination/illumination_geometry_engine.py`
- `src/worldgen/galaxy/galaxy_object_stub_generator.py`
- `src/worldgen/mw/mw_system_refiner_l2.py`

## Scorecard

- `src/astro/illumination/illumination_geometry_engine.py` disposition=`canonical` rank=`1` total_score=`52.32` risk=`HIGH`
- `src/worldgen/mw/mw_system_refiner_l2.py` disposition=`quarantine` rank=`2` total_score=`50.82` risk=`HIGH`
- `src/worldgen/galaxy/galaxy_object_stub_generator.py` disposition=`quarantine` rank=`3` total_score=`49.44` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/NUMERIC_DISCIPLINE0_RETRO_AUDIT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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
