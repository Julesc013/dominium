Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.11b04bf412706cb4`

- Symbol: `_write_bytes`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/setup/setup_install_tests.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tests/setup/install_manifest_tests.py`
- `tests/setup/setup_install_tests.py`

## Scorecard

- `tests/setup/setup_install_tests.py` disposition=`canonical` rank=`1` total_score=`79.36` risk=`HIGH`
- `tests/setup/install_manifest_tests.py` disposition=`quarantine` rank=`2` total_score=`77.33` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/CLI_CONTRACTS.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/INVARIANT_REGISTRY.md, docs/architecture/REPO_NAV.md, docs/architecture/VALIDATION_RULES.md, docs/audit/CANON_MAP.md, docs/audit/DOCS_AUDIT_PROMPT0.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
