Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.ae2fa23b3c149a9f`

- Symbol: `_sorted_unique_strings`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/control/tool_run_control_stress.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/control/capability/capability_engine.py`
- `src/control/control_plane_engine.py`
- `src/control/effects/effect_engine.py`
- `src/control/fidelity/fidelity_engine.py`
- `src/control/ir/control_ir_compiler.py`
- `src/control/ir/control_ir_programs.py`
- `src/control/ir/control_ir_verifier.py`
- `src/control/negotiation/negotiation_kernel.py`
- `src/control/planning/plan_engine.py`
- `src/control/view/view_engine.py`
- `src/fields/field_engine.py`
- `src/infrastructure/formalization/inference_engine.py`
- `src/inspection/inspection_engine.py`
- `src/interaction/action_surface_engine.py`
- `src/interaction/mount/mount_engine.py`
- `src/interaction/pose/pose_engine.py`
- `src/interaction/task/task_engine.py`
- `src/machines/port_engine.py`
- `src/materials/commitments/commitment_engine.py`
- `src/materials/provenance/event_stream_index.py`
- `src/mechanics/structural_graph_engine.py`
- `src/specs/spec_engine.py`
- `tools/control/tool_determinism_compare.py`
- `tools/control/tool_global_control_stress.py`
- `tools/control/tool_run_control_stress.py`

## Scorecard

- `tools/control/tool_run_control_stress.py` disposition=`canonical` rank=`1` total_score=`62.58` risk=`HIGH`
- `src/control/capability/capability_engine.py` disposition=`quarantine` rank=`2` total_score=`61.96` risk=`HIGH`
- `src/specs/spec_engine.py` disposition=`quarantine` rank=`3` total_score=`59.58` risk=`HIGH`
- `tools/control/tool_global_control_stress.py` disposition=`quarantine` rank=`4` total_score=`59.09` risk=`HIGH`
- `src/control/view/view_engine.py` disposition=`quarantine` rank=`5` total_score=`58.63` risk=`HIGH`
- `src/control/fidelity/fidelity_engine.py` disposition=`quarantine` rank=`6` total_score=`58.62` risk=`HIGH`
- `src/inspection/inspection_engine.py` disposition=`quarantine` rank=`7` total_score=`57.68` risk=`HIGH`
- `src/materials/commitments/commitment_engine.py` disposition=`quarantine` rank=`8` total_score=`57.32` risk=`HIGH`
- `src/fields/field_engine.py` disposition=`quarantine` rank=`9` total_score=`56.61` risk=`HIGH`
- `src/interaction/pose/pose_engine.py` disposition=`quarantine` rank=`10` total_score=`56.56` risk=`HIGH`
- `tools/control/tool_determinism_compare.py` disposition=`quarantine` rank=`11` total_score=`55.83` risk=`HIGH`
- `src/materials/provenance/event_stream_index.py` disposition=`quarantine` rank=`12` total_score=`54.95` risk=`HIGH`
- `src/interaction/mount/mount_engine.py` disposition=`quarantine` rank=`13` total_score=`54.63` risk=`HIGH`
- `src/interaction/task/task_engine.py` disposition=`quarantine` rank=`14` total_score=`54.12` risk=`HIGH`
- `src/control/ir/control_ir_verifier.py` disposition=`quarantine` rank=`15` total_score=`53.99` risk=`HIGH`
- `src/machines/port_engine.py` disposition=`quarantine` rank=`16` total_score=`53.01` risk=`HIGH`
- `src/control/ir/control_ir_programs.py` disposition=`drop` rank=`17` total_score=`51.89` risk=`HIGH`
- `src/infrastructure/formalization/inference_engine.py` disposition=`drop` rank=`18` total_score=`51.42` risk=`HIGH`
- `src/control/ir/control_ir_compiler.py` disposition=`merge` rank=`19` total_score=`51.26` risk=`HIGH`
- `src/interaction/action_surface_engine.py` disposition=`drop` rank=`20` total_score=`50.36` risk=`HIGH`
- `src/control/negotiation/negotiation_kernel.py` disposition=`drop` rank=`21` total_score=`49.49` risk=`HIGH`
- `src/control/effects/effect_engine.py` disposition=`drop` rank=`22` total_score=`46.67` risk=`HIGH`
- `src/mechanics/structural_graph_engine.py` disposition=`drop` rank=`23` total_score=`46.4` risk=`HIGH`
- `src/control/control_plane_engine.py` disposition=`merge` rank=`24` total_score=`46.01` risk=`HIGH`
- `src/control/planning/plan_engine.py` disposition=`merge` rank=`25` total_score=`42.73` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/audit/REPO_TREE_INDEX.md`

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
