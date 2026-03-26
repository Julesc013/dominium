Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.0dd5a43f92086112`

- Symbol: `BASELINE_DOC_REL`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/meta/identity_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/compat/migration_lifecycle_common.py`
- `tools/engine/concurrency_contract_common.py`
- `tools/engine/numeric_discipline_common.py`
- `tools/governance/governance_model_common.py`
- `tools/lib/store_gc_common.py`
- `tools/meta/identity_common.py`
- `tools/meta/observability_common.py`
- `tools/perf/performance_envelope_common.py`
- `tools/release/archive_policy_common.py`
- `tools/release/install_profile_common.py`
- `tools/release/release_index_policy_common.py`
- `tools/release/update_model_common.py`
- `tools/security/trust_model_common.py`

## Scorecard

- `tools/meta/identity_common.py` disposition=`canonical` rank=`1` total_score=`87.38` risk=`HIGH`
- `tools/release/archive_policy_common.py` disposition=`quarantine` rank=`2` total_score=`79.88` risk=`HIGH`
- `tools/release/release_index_policy_common.py` disposition=`quarantine` rank=`3` total_score=`78.69` risk=`HIGH`
- `tools/release/install_profile_common.py` disposition=`merge` rank=`4` total_score=`75.83` risk=`HIGH`
- `tools/release/update_model_common.py` disposition=`merge` rank=`5` total_score=`75.12` risk=`HIGH`
- `tools/perf/performance_envelope_common.py` disposition=`merge` rank=`6` total_score=`74.08` risk=`HIGH`
- `tools/lib/store_gc_common.py` disposition=`merge` rank=`7` total_score=`74.05` risk=`HIGH`
- `tools/security/trust_model_common.py` disposition=`merge` rank=`8` total_score=`73.63` risk=`HIGH`
- `tools/governance/governance_model_common.py` disposition=`merge` rank=`9` total_score=`72.98` risk=`HIGH`
- `tools/compat/migration_lifecycle_common.py` disposition=`merge` rank=`10` total_score=`72.74` risk=`HIGH`
- `tools/meta/observability_common.py` disposition=`merge` rank=`11` total_score=`68.52` risk=`HIGH`
- `tools/engine/concurrency_contract_common.py` disposition=`merge` rank=`12` total_score=`66.67` risk=`HIGH`
- `tools/engine/numeric_discipline_common.py` disposition=`merge` rank=`13` total_score=`63.67` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/INSTALL_MODEL.md, docs/architecture/INSTANCE_MODEL.md, docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/architecture/SAVE_MODEL.md`

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
