Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c501e5439d421bfb`

- Symbol: `dom_schema_id_for_domain`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/include/domino/io/schema_registry.h`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/include/domino/io/schema_registry.h`
- `engine/modules/io/schema_registry.c`

## Scorecard

- `engine/include/domino/io/schema_registry.h` disposition=`canonical` rank=`1` total_score=`84.88` risk=`HIGH`
- `engine/modules/io/schema_registry.c` disposition=`quarantine` rank=`2` total_score=`79.17` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/COMPONENTS.md, docs/audit/CONTROL_PLANE_ENFORCEMENT_BASELINE.md, docs/audit/DOMAIN_FOUNDATION_REPORT.md, docs/audit/FIELD_LAYER_BASELINE.md, docs/audit/PROMPT_G_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SAFETY_PATTERN_BASELINE.md`

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
