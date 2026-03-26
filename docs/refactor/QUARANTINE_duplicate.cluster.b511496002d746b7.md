Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.b511496002d746b7`

- Symbol: `_as_list`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/process/tool_replay_capsule_window.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/appshell/supervisor/supervisor_engine.py`
- `src/appshell/tui/tui_engine.py`
- `src/astro/ephemeris/kepler_proxy_engine.py`
- `src/astro/illumination/illumination_geometry_engine.py`
- `src/astro/views/orbit_view_engine.py`
- `src/client/ui/inspect_panels.py`
- `src/client/ui/teleport_controller.py`
- `src/client/ui/viewer_shell.py`
- `src/embodiment/body/body_system.py`
- `src/embodiment/lens/camera_smoothing.py`
- `src/embodiment/lens/lens_engine.py`
- `src/embodiment/movement/jump_process.py`
- `src/geo/kernel/geo_kernel.py`
- `src/logic/compile/logic_proof_engine.py`
- `src/logic/debug/debug_engine.py`
- `src/logic/debug/runtime_state.py`
- `src/logic/element/instrumentation_binding.py`
- `src/logic/element/logic_element_validator.py`
- `src/logic/eval/degradation_policy.py`
- `src/logic/fault/fault_engine.py`
- `src/logic/network/instrumentation_binding.py`
- `src/logic/protocol/rows.py`
- `src/meta/compile/compile_engine.py`
- `src/meta/compute/compute_budget_engine.py`
- `src/meta/instrumentation/instrumentation_engine.py`
- `src/meta/numeric.py`
- `src/meta/profile/profile_engine.py`
- `src/meta/stability/stability_validator.py`
- `src/numeric_discipline.py`
- `src/process/capsules/capsule_builder.py`
- `src/process/capsules/capsule_executor.py`
- `src/process/drift/drift_engine.py`
- `src/process/maturity/maturity_engine.py`
- `src/process/maturity/metrics_engine.py`
- `src/process/process_definition_validator.py`
- `src/process/process_run_engine.py`
- `src/process/qc/qc_engine.py`
- `src/process/research/experiment_engine.py`
- `src/process/research/inference_engine.py`
- `src/process/software/pipeline_engine.py`
- `src/system/certification/system_cert_engine.py`
- `src/system/forensics/system_forensics_engine.py`
- `src/system/macro/macro_capsule_engine.py`
- `src/system/reliability/reliability_engine.py`
- `src/system/reliability/system_health_engine.py`
- `src/system/statevec/statevec_engine.py`
- `src/system/templates/template_compiler.py`
- `src/ui/ui_model.py`
- `src/validation/validation_engine.py`
- `tools/appshell/appshell6_probe.py`
- `tools/astro/sol2_runtime_common.py`
- `tools/convergence/convergence_gate_common.py`
- `tools/dist/dist6_interop_common.py`
- `tools/dist/dist_verify_common.py`
- `tools/logic/tool_replay_trace_window.py`
- `tools/logic/tool_run_logic_stress.py`
- `tools/mvp/cross_platform_gate_common.py`
- `tools/mvp/disaster_suite_common.py`
- `tools/mvp/ecosystem_verify_common.py`
- `tools/mvp/gameplay_loop_common.py`
- `tools/mvp/mvp_smoke_common.py`
- `tools/mvp/stress_gate_common.py`
- `tools/mvp/toolchain_matrix_common.py`
- `tools/mvp/update_sim_common.py`
- `tools/process/tool_replay_capsule_window.py`
- `tools/process/tool_replay_drift_window.py`
- `tools/process/tool_replay_experiment_window.py`
- `tools/process/tool_replay_maturity_window.py`
- `tools/process/tool_replay_pipeline_window.py`
- `tools/process/tool_replay_proc_window.py`
- `tools/process/tool_replay_qc_window.py`
- `tools/process/tool_replay_quality_window.py`
- `tools/process/tool_replay_reverse_engineering_window.py`
- `tools/release/offline_archive_common.py`
- `tools/security/trust_strict_common.py`

## Scorecard

- `tools/process/tool_replay_capsule_window.py` disposition=`canonical` rank=`1` total_score=`88.33` risk=`HIGH`
- `tools/process/tool_replay_qc_window.py` disposition=`quarantine` rank=`2` total_score=`87.8` risk=`HIGH`
- `tools/process/tool_replay_quality_window.py` disposition=`quarantine` rank=`3` total_score=`87.8` risk=`HIGH`
- `tools/dist/dist_verify_common.py` disposition=`quarantine` rank=`4` total_score=`87.32` risk=`HIGH`
- `tools/mvp/ecosystem_verify_common.py` disposition=`quarantine` rank=`5` total_score=`84.11` risk=`HIGH`
- `tools/process/tool_replay_proc_window.py` disposition=`quarantine` rank=`6` total_score=`83.21` risk=`HIGH`
- `tools/release/offline_archive_common.py` disposition=`quarantine` rank=`7` total_score=`83.04` risk=`HIGH`
- `tools/mvp/disaster_suite_common.py` disposition=`quarantine` rank=`8` total_score=`82.26` risk=`HIGH`
- `tools/mvp/gameplay_loop_common.py` disposition=`quarantine` rank=`9` total_score=`82.26` risk=`HIGH`
- `tools/mvp/mvp_smoke_common.py` disposition=`quarantine` rank=`10` total_score=`81.79` risk=`HIGH`
- `tools/mvp/cross_platform_gate_common.py` disposition=`quarantine` rank=`11` total_score=`81.43` risk=`HIGH`
- `tools/appshell/appshell6_probe.py` disposition=`quarantine` rank=`12` total_score=`79.99` risk=`HIGH`
- `src/meta/numeric.py` disposition=`quarantine` rank=`13` total_score=`79.64` risk=`HIGH`
- `tools/dist/dist6_interop_common.py` disposition=`merge` rank=`14` total_score=`78.21` risk=`HIGH`
- `tools/mvp/toolchain_matrix_common.py` disposition=`merge` rank=`15` total_score=`77.85` risk=`HIGH`
- `tools/security/trust_strict_common.py` disposition=`merge` rank=`16` total_score=`77.8` risk=`HIGH`
- `tools/process/tool_replay_maturity_window.py` disposition=`drop` rank=`17` total_score=`77.76` risk=`HIGH`
- `src/process/maturity/metrics_engine.py` disposition=`merge` rank=`18` total_score=`77.62` risk=`HIGH`
- `tools/logic/tool_replay_trace_window.py` disposition=`merge` rank=`19` total_score=`76.73` risk=`HIGH`
- `tools/mvp/stress_gate_common.py` disposition=`merge` rank=`20` total_score=`76.49` risk=`HIGH`
- `tools/process/tool_replay_drift_window.py` disposition=`drop` rank=`21` total_score=`75.89` risk=`HIGH`
- `tools/process/tool_replay_pipeline_window.py` disposition=`merge` rank=`22` total_score=`75.89` risk=`HIGH`
- `tools/logic/tool_run_logic_stress.py` disposition=`merge` rank=`23` total_score=`75.71` risk=`HIGH`
- `src/process/maturity/maturity_engine.py` disposition=`drop` rank=`24` total_score=`75.48` risk=`HIGH`
- `src/meta/profile/profile_engine.py` disposition=`drop` rank=`25` total_score=`73.87` risk=`HIGH`
- `src/process/drift/drift_engine.py` disposition=`drop` rank=`26` total_score=`73.87` risk=`HIGH`
- `src/embodiment/body/body_system.py` disposition=`drop` rank=`27` total_score=`71.85` risk=`HIGH`
- `tools/convergence/convergence_gate_common.py` disposition=`merge` rank=`28` total_score=`71.61` risk=`HIGH`
- `src/process/process_run_engine.py` disposition=`drop` rank=`29` total_score=`71.25` risk=`HIGH`
- `tools/process/tool_replay_experiment_window.py` disposition=`merge` rank=`30` total_score=`70.96` risk=`HIGH`
- `src/logic/debug/runtime_state.py` disposition=`drop` rank=`31` total_score=`70.83` risk=`HIGH`
- `src/meta/compile/compile_engine.py` disposition=`drop` rank=`32` total_score=`70.36` risk=`HIGH`
- `tools/mvp/update_sim_common.py` disposition=`merge` rank=`33` total_score=`70.14` risk=`HIGH`
- `tools/process/tool_replay_reverse_engineering_window.py` disposition=`merge` rank=`34` total_score=`70.0` risk=`HIGH`
- `src/process/qc/qc_engine.py` disposition=`drop` rank=`35` total_score=`69.76` risk=`HIGH`
- `src/logic/eval/degradation_policy.py` disposition=`drop` rank=`36` total_score=`69.11` risk=`HIGH`
- `src/logic/protocol/rows.py` disposition=`drop` rank=`37` total_score=`68.69` risk=`HIGH`
- `src/process/capsules/capsule_builder.py` disposition=`drop` rank=`38` total_score=`68.57` risk=`HIGH`
- `src/ui/ui_model.py` disposition=`drop` rank=`39` total_score=`68.57` risk=`HIGH`
- `src/system/statevec/statevec_engine.py` disposition=`drop` rank=`40` total_score=`68.15` risk=`HIGH`
- `src/embodiment/lens/lens_engine.py` disposition=`drop` rank=`41` total_score=`67.26` risk=`HIGH`
- `src/appshell/tui/tui_engine.py` disposition=`drop` rank=`42` total_score=`66.19` risk=`HIGH`
- `src/process/process_definition_validator.py` disposition=`drop` rank=`43` total_score=`65.95` risk=`HIGH`
- `src/meta/compute/compute_budget_engine.py` disposition=`drop` rank=`44` total_score=`64.34` risk=`HIGH`
- `src/system/macro/macro_capsule_engine.py` disposition=`drop` rank=`45` total_score=`64.05` risk=`HIGH`
- `src/client/ui/viewer_shell.py` disposition=`drop` rank=`46` total_score=`62.56` risk=`HIGH`
- `src/meta/instrumentation/instrumentation_engine.py` disposition=`drop` rank=`47` total_score=`62.32` risk=`HIGH`
- `src/system/reliability/reliability_engine.py` disposition=`drop` rank=`48` total_score=`62.32` risk=`HIGH`
- `src/astro/illumination/illumination_geometry_engine.py` disposition=`drop` rank=`49` total_score=`61.9` risk=`HIGH`
- `src/system/certification/system_cert_engine.py` disposition=`drop` rank=`50` total_score=`61.71` risk=`HIGH`
- `tools/astro/sol2_runtime_common.py` disposition=`merge` rank=`51` total_score=`61.48` risk=`HIGH`
- `src/numeric_discipline.py` disposition=`drop` rank=`52` total_score=`61.2` risk=`HIGH`
- `src/client/ui/inspect_panels.py` disposition=`drop` rank=`53` total_score=`60.46` risk=`HIGH`
- `src/system/forensics/system_forensics_engine.py` disposition=`drop` rank=`54` total_score=`60.04` risk=`HIGH`
- `src/meta/stability/stability_validator.py` disposition=`drop` rank=`55` total_score=`59.4` risk=`HIGH`
- `src/logic/network/instrumentation_binding.py` disposition=`drop` rank=`56` total_score=`59.08` risk=`HIGH`
- `src/system/reliability/system_health_engine.py` disposition=`drop` rank=`57` total_score=`59.07` risk=`HIGH`
- `src/logic/element/instrumentation_binding.py` disposition=`drop` rank=`58` total_score=`58.64` risk=`HIGH`
- `src/system/templates/template_compiler.py` disposition=`drop` rank=`59` total_score=`57.68` risk=`HIGH`
- `src/geo/kernel/geo_kernel.py` disposition=`drop` rank=`60` total_score=`57.62` risk=`HIGH`
- `src/client/ui/teleport_controller.py` disposition=`drop` rank=`61` total_score=`57.26` risk=`HIGH`
- `src/astro/views/orbit_view_engine.py` disposition=`drop` rank=`62` total_score=`56.07` risk=`HIGH`
- `src/embodiment/lens/camera_smoothing.py` disposition=`drop` rank=`63` total_score=`55.73` risk=`HIGH`
- `src/process/research/inference_engine.py` disposition=`drop` rank=`64` total_score=`55.73` risk=`HIGH`
- `src/appshell/supervisor/supervisor_engine.py` disposition=`drop` rank=`65` total_score=`55.65` risk=`HIGH`
- `src/logic/element/logic_element_validator.py` disposition=`drop` rank=`66` total_score=`55.58` risk=`HIGH`
- `src/logic/debug/debug_engine.py` disposition=`drop` rank=`67` total_score=`55.18` risk=`HIGH`
- `src/process/research/experiment_engine.py` disposition=`drop` rank=`68` total_score=`54.76` risk=`HIGH`
- `src/logic/fault/fault_engine.py` disposition=`drop` rank=`69` total_score=`54.58` risk=`HIGH`
- `src/process/software/pipeline_engine.py` disposition=`drop` rank=`70` total_score=`54.35` risk=`HIGH`
- `src/process/capsules/capsule_executor.py` disposition=`drop` rank=`71` total_score=`53.75` risk=`HIGH`
- `src/astro/ephemeris/kepler_proxy_engine.py` disposition=`drop` rank=`72` total_score=`52.89` risk=`HIGH`
- `src/embodiment/movement/jump_process.py` disposition=`drop` rank=`73` total_score=`52.83` risk=`HIGH`
- `src/logic/compile/logic_proof_engine.py` disposition=`drop` rank=`74` total_score=`52.38` risk=`HIGH`
- `src/validation/validation_engine.py` disposition=`drop` rank=`75` total_score=`50.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/appshell/CLI_REFERENCE.md, docs/appshell/TOOL_REFERENCE.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/LOCKLIST.md, docs/architecture/RISK_AND_LIABILITY_MODEL.md`

## Tests Involved

- `python tools/appshell/tool_run_supervisor_hardening.py --repo-root .`
- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
