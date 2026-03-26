Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.03b6e9358e8b4b84`

- Symbol: `_base_state`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_spec_apply_deterministic.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_compliance_result_deterministic.py`
- `tools/xstack/testx/tests/test_epistemic_redaction_field_values.py`
- `tools/xstack/testx/tests/test_interest_region_selection_determinism.py`
- `tools/xstack/testx/tests/test_no_spec_packs_null_boot_ok.py`
- `tools/xstack/testx/tests/test_spec_apply_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_spec_apply_deterministic.py` disposition=`canonical` rank=`1` total_score=`81.77` risk=`HIGH`
- `tools/xstack/testx/tests/test_compliance_result_deterministic.py` disposition=`quarantine` rank=`2` total_score=`75.99` risk=`HIGH`
- `tools/xstack/testx/tests/test_epistemic_redaction_field_values.py` disposition=`drop` rank=`3` total_score=`66.57` risk=`HIGH`
- `tools/xstack/testx/tests/test_interest_region_selection_determinism.py` disposition=`merge` rank=`4` total_score=`66.32` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_spec_packs_null_boot_ok.py` disposition=`drop` rank=`5` total_score=`65.5` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/archive/ci/PHASE6_AUDIT_REPORT.md, docs/archive/repox/APRX_INVENTORY.md, docs/audit/CANON_MAP.md, docs/audit/DETERMINISM_ENVELOPE_REPORT.md, docs/audit/DOCS_AUDIT_PROMPT0.md, docs/audit/DOC_INDEX.md`

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
