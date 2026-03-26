Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0220ca92e378100c`

- Symbol: `d_struct_validate`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/struct/d_struct.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/struct/d_struct.h`
- `engine/modules/struct/d_struct_validate.c`

## Scorecard

- `engine/modules/struct/d_struct.h` disposition=`canonical` rank=`1` total_score=`79.88` risk=`HIGH`
- `engine/modules/struct/d_struct_validate.c` disposition=`quarantine` rank=`2` total_score=`77.86` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/HYGIENE_QUEUE.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/DATA_FORMATS.md, docs/specs/SPEC_BUILD.md, docs/specs/SPEC_CORE.md, docs/specs/SPEC_DUI.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
