Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.f53d6856dd5b4259`

- Symbol: `_request`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_inspection_snapshot_redaction.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_budget_degrade_to_alarms.py`
- `tools/xstack/testx/tests/test_epistemic_gating_of_inferred_overlays.py`
- `tools/xstack/testx/tests/test_epistemic_redaction_of_values.py`
- `tools/xstack/testx/tests/test_inspection_snapshot_redaction.py`
- `tools/xstack/testx/tests/test_view_negotiation_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_inspection_snapshot_redaction.py` disposition=`canonical` rank=`1` total_score=`71.33` risk=`HIGH`
- `tools/xstack/testx/tests/test_epistemic_redaction_of_values.py` disposition=`quarantine` rank=`2` total_score=`68.95` risk=`HIGH`
- `tools/xstack/testx/tests/test_view_negotiation_deterministic.py` disposition=`quarantine` rank=`3` total_score=`65.51` risk=`HIGH`
- `tools/xstack/testx/tests/test_budget_degrade_to_alarms.py` disposition=`quarantine` rank=`4` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_epistemic_gating_of_inferred_overlays.py` disposition=`merge` rank=`5` total_score=`58.21` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/INSPECTION_SYSTEM_BASELINE.md, docs/audit/INTERIOR_DIEGETIC_INSPECTION_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/UX0_RETRO_AUDIT.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
