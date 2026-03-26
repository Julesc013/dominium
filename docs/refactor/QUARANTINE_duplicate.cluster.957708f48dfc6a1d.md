Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.957708f48dfc6a1d`

- Symbol: `_normalize_value`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/lib/instance/instance_validator.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/lib/artifact/artifact_validator.py`
- `src/lib/install/install_validator.py`
- `src/lib/instance/instance_validator.py`
- `src/lib/save/save_validator.py`

## Scorecard

- `src/lib/instance/instance_validator.py` disposition=`canonical` rank=`1` total_score=`70.77` risk=`HIGH`
- `src/lib/artifact/artifact_validator.py` disposition=`quarantine` rank=`2` total_score=`69.82` risk=`HIGH`
- `src/lib/save/save_validator.py` disposition=`quarantine` rank=`3` total_score=`69.7` risk=`HIGH`
- `src/lib/install/install_validator.py` disposition=`merge` rank=`4` total_score=`58.27` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/architecture/INVARIANT_REGISTRY.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/audit/CONTENT_STORE_BASELINE.md, docs/audit/DOC_INDEX.md, docs/audit/ECOSYSTEM_VERIFY0_RETRO_AUDIT.md, docs/audit/GR3_FAST_RESULTS.md, docs/audit/INSTALL_MANIFEST_BASELINE.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
