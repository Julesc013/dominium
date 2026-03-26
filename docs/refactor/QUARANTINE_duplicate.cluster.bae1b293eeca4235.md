Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.bae1b293eeca4235`

- Symbol: `d_world`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/core/d_subsystem.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/core/d_subsystem.h`
- `engine/modules/world/d_serialize.c`
- `engine/modules/world/d_serialize.h`
- `engine/modules/world/d_worldgen.h`

## Scorecard

- `engine/modules/core/d_subsystem.h` disposition=`canonical` rank=`1` total_score=`90.48` risk=`HIGH`
- `engine/modules/world/d_worldgen.h` disposition=`quarantine` rank=`2` total_score=`89.4` risk=`HIGH`
- `engine/modules/world/d_serialize.h` disposition=`quarantine` rank=`3` total_score=`87.38` risk=`HIGH`
- `engine/modules/world/d_serialize.c` disposition=`quarantine` rank=`4` total_score=`84.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/architecture/DIRECTORY_CONTEXT.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/RNG_MODEL.md, docs/archive/ci/DOCS_VALIDATION_REPORT.md, docs/audit/DOC_INDEX.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md`

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
