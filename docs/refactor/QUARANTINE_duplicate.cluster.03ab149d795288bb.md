Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.03ab149d795288bb`

- Symbol: `normalize_list`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/distribution/profile_inspect.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/distribution/compat_dry_run.py`
- `tools/distribution/lockfile_inspect.py`
- `tools/distribution/profile_inspect.py`
- `tools/fab/fab_inspect.py`
- `tools/fab/fab_validate.py`
- `tools/pack/capability_inspect.py`
- `tools/pack/migrate_capability_gating.py`
- `tools/pack/pack_validate.py`

## Scorecard

- `tools/distribution/profile_inspect.py` disposition=`canonical` rank=`1` total_score=`87.62` risk=`HIGH`
- `tools/distribution/compat_dry_run.py` disposition=`quarantine` rank=`2` total_score=`81.83` risk=`HIGH`
- `tools/pack/pack_validate.py` disposition=`quarantine` rank=`3` total_score=`81.55` risk=`HIGH`
- `tools/fab/fab_validate.py` disposition=`merge` rank=`4` total_score=`80.44` risk=`HIGH`
- `tools/pack/capability_inspect.py` disposition=`quarantine` rank=`5` total_score=`79.05` risk=`HIGH`
- `tools/distribution/lockfile_inspect.py` disposition=`drop` rank=`6` total_score=`75.65` risk=`HIGH`
- `tools/fab/fab_inspect.py` disposition=`merge` rank=`7` total_score=`75.59` risk=`HIGH`
- `tools/pack/migrate_capability_gating.py` disposition=`merge` rank=`8` total_score=`66.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/INSTANCE_MODEL.md, docs/architecture/PRODUCT_SHELL_CONTRACT.md, docs/architecture/SAVE_MODEL.md, docs/audit/CANON_MAP.md, docs/audit/COMPONENT_GRAPH0_RETRO_AUDIT.md, docs/audit/DETERMINISM_AND_PERFORMANCE_BASELINE.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
