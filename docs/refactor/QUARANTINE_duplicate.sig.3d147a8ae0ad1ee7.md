Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3d147a8ae0ad1ee7`

- Symbol: `normalize_path`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/launcher/launcher_cli.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `setup/packages/scripts/doc_ratio_check.py`
- `tools/launcher/launcher_cli.py`
- `tools/ops/ops_cli.py`
- `tools/setup/setup_cli.py`

## Scorecard

- `tools/launcher/launcher_cli.py` disposition=`canonical` rank=`1` total_score=`69.46` risk=`HIGH`
- `setup/packages/scripts/doc_ratio_check.py` disposition=`merge` rank=`2` total_score=`64.29` risk=`HIGH`
- `tools/setup/setup_cli.py` disposition=`quarantine` rank=`3` total_score=`61.61` risk=`HIGH`
- `tools/ops/ops_cli.py` disposition=`quarantine` rank=`4` total_score=`60.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/app/CLI_CONTRACTS.md, docs/app/ENGINE_GAME_DIAGNOSTICS.md, docs/app/IDE_WORKFLOW.md, docs/app/NATIVE_UI_POLICY.md, docs/app/PRODUCT_BOUNDARIES.md, docs/app/RUNTIME_LOOP.md, docs/app/TESTX_COMPLIANCE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
