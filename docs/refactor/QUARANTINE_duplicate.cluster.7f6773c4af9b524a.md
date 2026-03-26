Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.7f6773c4af9b524a`

- Symbol: `_loss_registry`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_message_delivery_deterministic.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_acceptance_threshold.py`
- `tools/xstack/testx/tests/test_capacity_queueing_deterministic.py`
- `tools/xstack/testx/tests/test_courier_channel_delivery_matches_mob_arrival.py`
- `tools/xstack/testx/tests/test_delay_accumulation_deterministic.py`
- `tools/xstack/testx/tests/test_message_delivery_deterministic.py`
- `tools/xstack/testx/tests/test_no_direct_delivery.py`
- `tools/xstack/testx/tests/test_receipt_idempotent.py`
- `tools/xstack/testx/tests/test_receipt_weighted_by_trust.py`
- `tools/xstack/testx/tests/test_report_acceptance_depends_on_trust.py`
- `tools/xstack/testx/tests/test_routing_cache_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_message_delivery_deterministic.py` disposition=`canonical` rank=`1` total_score=`73.71` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_direct_delivery.py` disposition=`quarantine` rank=`2` total_score=`66.57` risk=`HIGH`
- `tools/xstack/testx/tests/test_delay_accumulation_deterministic.py` disposition=`merge` rank=`3` total_score=`64.19` risk=`HIGH`
- `tools/xstack/testx/tests/test_receipt_weighted_by_trust.py` disposition=`drop` rank=`4` total_score=`64.19` risk=`HIGH`
- `tools/xstack/testx/tests/test_routing_cache_deterministic.py` disposition=`merge` rank=`5` total_score=`64.19` risk=`HIGH`
- `tools/xstack/testx/tests/test_acceptance_threshold.py` disposition=`merge` rank=`6` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_capacity_queueing_deterministic.py` disposition=`merge` rank=`7` total_score=`62.26` risk=`HIGH`
- `tools/xstack/testx/tests/test_courier_channel_delivery_matches_mob_arrival.py` disposition=`merge` rank=`8` total_score=`62.26` risk=`HIGH`
- `tools/xstack/testx/tests/test_report_acceptance_depends_on_trust.py` disposition=`merge` rank=`9` total_score=`62.26` risk=`HIGH`
- `tools/xstack/testx/tests/test_receipt_idempotent.py` disposition=`merge` rank=`10` total_score=`61.07` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/release/PROVISIONAL_FEATURE_LIST.md, docs/specs/SPEC_COMMUNICATION.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
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
