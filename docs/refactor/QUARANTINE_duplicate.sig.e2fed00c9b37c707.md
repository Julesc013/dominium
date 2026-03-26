Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e2fed00c9b37c707`

- Symbol: `load_pack_manifest`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tests/app/pack_resolution_tests.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tests/app/pack_resolution_tests.py`
- `tests/contentlib/contentlib_pack_contract_tests.py`
- `tests/data_1/data1_pack_contract_tests.py`

## Scorecard

- `tests/app/pack_resolution_tests.py` disposition=`canonical` rank=`1` total_score=`62.18` risk=`HIGH`
- `tests/data_1/data1_pack_contract_tests.py` disposition=`quarantine` rank=`2` total_score=`55.12` risk=`HIGH`
- `tests/contentlib/contentlib_pack_contract_tests.py` disposition=`merge` rank=`3` total_score=`50.71` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/architecture/INVARIANT_REGISTRY.md, docs/audit/CANON_MAP.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/DOCS_AUDIT_PROMPT0.md, docs/audit/DOC_INDEX.md, docs/audit/RECOMMENDED_NEXT_FIXES.md, docs/audit/REPO_TREE_INDEX.md`

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
