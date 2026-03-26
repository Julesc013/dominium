Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.73f5830efa7cb7fd`

- Symbol: `_norm_rel`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/dist/dist_verify_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/dist/clean_room_common.py`
- `tools/dist/dist6_interop_common.py`
- `tools/dist/dist_platform_matrix_common.py`
- `tools/dist/dist_verify_common.py`
- `tools/release/distribution_model_common.py`

## Scorecard

- `tools/dist/dist_verify_common.py` disposition=`canonical` rank=`1` total_score=`87.32` risk=`HIGH`
- `tools/dist/clean_room_common.py` disposition=`merge` rank=`2` total_score=`85.89` risk=`HIGH`
- `tools/dist/dist6_interop_common.py` disposition=`quarantine` rank=`3` total_score=`78.21` risk=`HIGH`
- `tools/dist/dist_platform_matrix_common.py` disposition=`merge` rank=`4` total_score=`75.89` risk=`HIGH`
- `tools/release/distribution_model_common.py` disposition=`merge` rank=`5` total_score=`72.02` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/XSTACK.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/setup_and_launcher.md, docs/archive/build/APR5_BUILD_INVENTORY.md, docs/audit/APPSHELL_BOOTSTRAP_BASELINE.md, docs/audit/ARCHIVE_OFFLINE0_RETRO_AUDIT.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
