Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f6b54689bb3490b4`

- Symbol: `dom_schema_registry`
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

- `engine/include/domino/io/schema_registry.h` disposition=`canonical` rank=`1` total_score=`87.26` risk=`HIGH`
- `engine/modules/io/schema_registry.c` disposition=`quarantine` rank=`2` total_score=`81.55` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/app/COMPATIBILITY_ENFORCEMENT.md, docs/app/READONLY_ADAPTER.md, docs/appshell/CLI_REFERENCE.md, docs/architecture/APP_CANON0.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/COMPONENTS.md, docs/archive/app/APR4_ENGINE_GAME_INTERFACE_INVENTORY.md`

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
