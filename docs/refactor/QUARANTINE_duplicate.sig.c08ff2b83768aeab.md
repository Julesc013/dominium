Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.c08ff2b83768aeab`

- Symbol: `cmd_validate`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/modpack/modpack_cli.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/modpack/modpack_cli.py`
- `tools/worldgen_offline/world_definition_cli.py`

## Scorecard

- `tools/modpack/modpack_cli.py` disposition=`canonical` rank=`1` total_score=`69.33` risk=`HIGH`
- `tools/worldgen_offline/world_definition_cli.py` disposition=`quarantine` rank=`2` total_score=`62.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md, docs/ci/HYGIENE_QUEUE.md`

## Tests Involved

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
