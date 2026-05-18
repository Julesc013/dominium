Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none

Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.da56f62535952322`

- Symbol: `d_content_structure_count`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `runtime/package/content/d_content.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `runtime/package/content/d_content.c`
- `runtime/package/content/d_content.h`

## Scorecard

- `runtime/package/content/d_content.h` disposition=`canonical` rank=`1` total_score=`74.52` risk=`HIGH`
- `runtime/package/content/d_content.c` disposition=`quarantine` rank=`2` total_score=`72.14` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/VALIDATION_RULES.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MVP_RUNTIME_BASELINE.md, docs/audit/PLANET_SURFACE_L3_BASELINE.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/WORLDGEN_LOCK_BASELINE.md, docs/canon/glossary_v1.md`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validators/suite/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
