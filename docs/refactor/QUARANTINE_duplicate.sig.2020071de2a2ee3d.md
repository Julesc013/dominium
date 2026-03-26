Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.2020071de2a2ee3d`

- Symbol: `_authority`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_observer_watermark_required.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_camera_bind_replay_determinism.py`
- `tools/xstack/testx/tests/test_camera_bind_requires_entitlement.py`
- `tools/xstack/testx/tests/test_inspection_cache_reuse.py`
- `tools/xstack/testx/tests/test_inspection_invalidation_on_state_change.py`
- `tools/xstack/testx/tests/test_observer_watermark_required.py`
- `tools/xstack/testx/tests/test_player_view_forbids_observer_lens.py`
- `tools/xstack/testx/tests/test_radio_delivery_deterministic.py`
- `tools/xstack/testx/tests/test_ranked_profile_forbids_free_view.py`
- `tools/xstack/testx/tests/test_ui_action_intent_mapping.py`
- `tools/xstack/testx/tests/test_view_requires_embodiment_refusal.py`

## Scorecard

- `tools/xstack/testx/tests/test_observer_watermark_required.py` disposition=`canonical` rank=`1` total_score=`78.02` risk=`HIGH`
- `tools/xstack/testx/tests/test_view_requires_embodiment_refusal.py` disposition=`quarantine` rank=`2` total_score=`78.02` risk=`HIGH`
- `tools/xstack/testx/tests/test_inspection_invalidation_on_state_change.py` disposition=`quarantine` rank=`3` total_score=`73.61` risk=`HIGH`
- `tools/xstack/testx/tests/test_ui_action_intent_mapping.py` disposition=`quarantine` rank=`4` total_score=`71.24` risk=`HIGH`
- `tools/xstack/testx/tests/test_camera_bind_replay_determinism.py` disposition=`quarantine` rank=`5` total_score=`68.95` risk=`HIGH`
- `tools/xstack/testx/tests/test_inspection_cache_reuse.py` disposition=`merge` rank=`6` total_score=`66.92` risk=`HIGH`
- `tools/xstack/testx/tests/test_camera_bind_requires_entitlement.py` disposition=`merge` rank=`7` total_score=`66.57` risk=`HIGH`
- `tools/xstack/testx/tests/test_player_view_forbids_observer_lens.py` disposition=`drop` rank=`8` total_score=`64.42` risk=`HIGH`
- `tools/xstack/testx/tests/test_radio_delivery_deterministic.py` disposition=`merge` rank=`9` total_score=`63.23` risk=`HIGH`
- `tools/xstack/testx/tests/test_ranked_profile_forbids_free_view.py` disposition=`merge` rank=`10` total_score=`62.03` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/governance/REPOX_RULESETS.md`

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
