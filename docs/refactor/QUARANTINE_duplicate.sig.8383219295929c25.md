Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.8383219295929c25`

- Symbol: `_to_int`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/control/tool_run_control_stress.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/client/interaction/affordance_generator.py`
- `src/client/interaction/inspection_overlays.py`
- `src/client/interaction/interaction_dispatch.py`
- `src/client/interaction/interaction_panel.py`
- `src/client/interaction/preview_generator.py`
- `src/control/control_plane_engine.py`
- `src/control/ir/control_ir_compiler.py`
- `src/control/ir/control_ir_verifier.py`
- `src/control/negotiation/negotiation_kernel.py`
- `src/control/proof/control_proof_bundle.py`
- `src/interaction/action_surface_engine.py`
- `tools/control/tool_determinism_compare.py`
- `tools/control/tool_global_control_stress.py`
- `tools/control/tool_run_control_stress.py`
- `worldgen/core/constraint_solver.py`

## Scorecard

- `tools/control/tool_run_control_stress.py` disposition=`canonical` rank=`1` total_score=`70.24` risk=`HIGH`
- `src/control/proof/control_proof_bundle.py` disposition=`quarantine` rank=`2` total_score=`68.87` risk=`HIGH`
- `tools/control/tool_global_control_stress.py` disposition=`quarantine` rank=`3` total_score=`65.79` risk=`HIGH`
- `worldgen/core/constraint_solver.py` disposition=`quarantine` rank=`4` total_score=`65.0` risk=`HIGH`
- `src/client/interaction/interaction_dispatch.py` disposition=`quarantine` rank=`5` total_score=`65.0` risk=`HIGH`
- `src/client/interaction/interaction_panel.py` disposition=`quarantine` rank=`6` total_score=`61.11` risk=`HIGH`
- `src/client/interaction/inspection_overlays.py` disposition=`quarantine` rank=`7` total_score=`61.07` risk=`HIGH`
- `src/control/ir/control_ir_verifier.py` disposition=`merge` rank=`8` total_score=`59.26` risk=`HIGH`
- `tools/control/tool_determinism_compare.py` disposition=`merge` rank=`9` total_score=`59.18` risk=`HIGH`
- `src/control/ir/control_ir_compiler.py` disposition=`merge` rank=`10` total_score=`58.92` risk=`HIGH`
- `src/client/interaction/affordance_generator.py` disposition=`merge` rank=`11` total_score=`58.81` risk=`HIGH`
- `src/interaction/action_surface_engine.py` disposition=`drop` rank=`12` total_score=`56.6` risk=`HIGH`
- `src/control/negotiation/negotiation_kernel.py` disposition=`drop` rank=`13` total_score=`53.8` risk=`HIGH`
- `src/client/interaction/preview_generator.py` disposition=`merge` rank=`14` total_score=`49.89` risk=`HIGH`
- `src/control/control_plane_engine.py` disposition=`drop` rank=`15` total_score=`47.94` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/FLUID_CONTAINMENT_BASELINE.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/TIME_ANCHOR0_RETRO_AUDIT.md, docs/governance/REPOX_RULESETS.md, docs/release/PROVISIONAL_FEATURE_LIST.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
