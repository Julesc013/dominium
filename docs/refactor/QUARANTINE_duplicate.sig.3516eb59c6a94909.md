Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.3516eb59c6a94909`

- Symbol: `_perceived_model`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/xstack/testx/tests/test_render_snapshot_schema_valid.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/xstack/testx/tests/test_backend_selection_fallback.py`
- `tools/xstack/testx/tests/test_epistemic_gating_of_inferred_overlays.py`
- `tools/xstack/testx/tests/test_no_assets_required.py`
- `tools/xstack/testx/tests/test_null_renderer_summary_deterministic.py`
- `tools/xstack/testx/tests/test_render_model_deterministic_ordering.py`
- `tools/xstack/testx/tests/test_render_proxy_fallback.py`
- `tools/xstack/testx/tests/test_render_snapshot_schema_valid.py`
- `tools/xstack/testx/tests/test_software_renderer_produces_image.py`
- `tools/xstack/testx/tests/test_surface_resolution_deterministic.py`

## Scorecard

- `tools/xstack/testx/tests/test_render_snapshot_schema_valid.py` disposition=`canonical` rank=`1` total_score=`76.45` risk=`HIGH`
- `tools/xstack/testx/tests/test_epistemic_gating_of_inferred_overlays.py` disposition=`quarantine` rank=`2` total_score=`71.08` risk=`HIGH`
- `tools/xstack/testx/tests/test_surface_resolution_deterministic.py` disposition=`quarantine` rank=`3` total_score=`68.95` risk=`HIGH`
- `tools/xstack/testx/tests/test_render_model_deterministic_ordering.py` disposition=`drop` rank=`4` total_score=`65.61` risk=`HIGH`
- `tools/xstack/testx/tests/test_render_proxy_fallback.py` disposition=`merge` rank=`5` total_score=`65.15` risk=`HIGH`
- `tools/xstack/testx/tests/test_no_assets_required.py` disposition=`drop` rank=`6` total_score=`64.64` risk=`HIGH`
- `tools/xstack/testx/tests/test_null_renderer_summary_deterministic.py` disposition=`drop` rank=`7` total_score=`63.58` risk=`HIGH`
- `tools/xstack/testx/tests/test_software_renderer_produces_image.py` disposition=`drop` rank=`8` total_score=`63.58` risk=`HIGH`
- `tools/xstack/testx/tests/test_backend_selection_fallback.py` disposition=`drop` rank=`9` total_score=`61.2` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/INTERACTION_UX_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/MULTIPLAYER_CONTRACT_FOUNDATION_REPORT.md, docs/audit/NETWORKGRAPH_STANDARD_BASELINE.md, docs/audit/REPO_TREE_INDEX.md`

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
