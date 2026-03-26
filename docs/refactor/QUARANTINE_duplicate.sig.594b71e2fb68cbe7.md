Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.594b71e2fb68cbe7`

- Symbol: `family_for_registry`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/meta/stability/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/meta/stability/__init__.py`
- `src/meta/stability/stability_scope.py`

## Scorecard

- `src/meta/stability/__init__.py` disposition=`canonical` rank=`1` total_score=`66.55` risk=`HIGH`
- `src/meta/stability/stability_scope.py` disposition=`quarantine` rank=`2` total_score=`59.25` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/XSTACK.md, docs/appshell/COMMANDS_AND_REFUSALS.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/EXTENSION_RULES.md, docs/architecture/GLOBAL_ID_MODEL.md, docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md, docs/architecture/ID_AND_NAMESPACE_RULES.md, docs/architecture/PROJECTION_LIFECYCLE.md`

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
