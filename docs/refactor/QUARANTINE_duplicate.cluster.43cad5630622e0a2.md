Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.43cad5630622e0a2`

- Symbol: `dom`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/validation/validator_common.h`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/coredata_compile/coredata_emit_tlv.cpp`
- `tools/coredata_compile/coredata_emit_tlv.h`
- `tools/coredata_compile/coredata_load.cpp`
- `tools/coredata_compile/coredata_load.h`
- `tools/coredata_compile/coredata_manifest.cpp`
- `tools/coredata_compile/coredata_manifest.h`
- `tools/coredata_compile/coredata_validate.cpp`
- `tools/coredata_compile/coredata_validate.h`
- `tools/coredata_validate/coredata_validate_checks.cpp`
- `tools/coredata_validate/coredata_validate_checks.h`
- `tools/coredata_validate/coredata_validate_load.cpp`
- `tools/coredata_validate/coredata_validate_load.h`
- `tools/coredata_validate/coredata_validate_report.cpp`
- `tools/coredata_validate/coredata_validate_report.h`
- `tools/mod_builder/dom_mod_builder_controller.cpp`
- `tools/mod_builder/dom_mod_builder_controller.h`
- `tools/modcheck/dom_modcheck.h`
- `tools/net_inspector/dom_net_inspector_controller.cpp`
- `tools/net_inspector/dom_net_inspector_controller.h`
- `tools/replay_analyzer/ra_diff.cpp`
- `tools/replay_analyzer/ra_diff.h`
- `tools/replay_analyzer/ra_parser.cpp`
- `tools/replay_analyzer/ra_parser.h`
- `tools/replay_viewer/dom_replay_viewer_controller.cpp`
- `tools/replay_viewer/dom_replay_viewer_controller.h`
- `tools/save_inspector/dom_save_inspector_controller.cpp`
- `tools/save_inspector/dom_save_inspector_controller.h`
- `tools/universe_editor/ue_commands.cpp`
- `tools/universe_editor/ue_commands.h`
- `tools/universe_editor/ue_queries.cpp`
- `tools/universe_editor/ue_queries.h`
- `tools/validate/policy_validation.cpp`
- `tools/validate/policy_validation.h`
- `tools/validate/tool_validation.cpp`
- `tools/validate/tool_validation.h`
- `tools/validation/validator_common.cpp`
- `tools/validation/validator_common.h`
- `tools/validation/validator_reports.cpp`
- `tools/validation/validator_reports.h`
- `tools/validation/validators_registry.cpp`
- `tools/validation/validators_registry.h`
- `tools/validator/validator_checks.cpp`
- `tools/validator/validator_checks.h`
- `tools/world_editor/dom_world_editor_controller.cpp`
- `tools/world_editor/dom_world_editor_controller.h`

## Scorecard

- `tools/validation/validator_common.h` disposition=`canonical` rank=`1` total_score=`80.6` risk=`HIGH`
- `tools/validate/policy_validation.h` disposition=`merge` rank=`2` total_score=`80.12` risk=`HIGH`
- `tools/validate/tool_validation.h` disposition=`merge` rank=`3` total_score=`80.12` risk=`HIGH`
- `tools/coredata_compile/coredata_manifest.h` disposition=`merge` rank=`4` total_score=`75.48` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_load.h` disposition=`merge` rank=`5` total_score=`74.93` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_report.h` disposition=`merge` rank=`6` total_score=`74.93` risk=`HIGH`
- `tools/coredata_compile/coredata_load.h` disposition=`merge` rank=`7` total_score=`74.58` risk=`HIGH`
- `tools/validate/policy_validation.cpp` disposition=`merge` rank=`8` total_score=`74.4` risk=`HIGH`
- `tools/validate/tool_validation.cpp` disposition=`merge` rank=`9` total_score=`74.4` risk=`HIGH`
- `tools/coredata_compile/coredata_validate.h` disposition=`merge` rank=`10` total_score=`72.58` risk=`HIGH`
- `tools/validation/validator_common.cpp` disposition=`merge` rank=`11` total_score=`71.05` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_report.cpp` disposition=`quarantine` rank=`12` total_score=`70.78` risk=`HIGH`
- `tools/validator/validator_checks.h` disposition=`merge` rank=`13` total_score=`70.44` risk=`HIGH`
- `tools/validation/validator_reports.h` disposition=`merge` rank=`14` total_score=`69.58` risk=`HIGH`
- `tools/coredata_compile/coredata_load.cpp` disposition=`merge` rank=`15` total_score=`69.13` risk=`HIGH`
- `tools/modcheck/dom_modcheck.h` disposition=`merge` rank=`16` total_score=`68.62` risk=`HIGH`
- `tools/coredata_compile/coredata_manifest.cpp` disposition=`merge` rank=`17` total_score=`68.06` risk=`HIGH`
- `tools/coredata_compile/coredata_validate.cpp` disposition=`merge` rank=`18` total_score=`67.67` risk=`HIGH`
- `tools/validation/validators_registry.h` disposition=`merge` rank=`19` total_score=`67.65` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_load.cpp` disposition=`merge` rank=`20` total_score=`66.13` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_checks.h` disposition=`merge` rank=`21` total_score=`66.1` risk=`HIGH`
- `tools/save_inspector/dom_save_inspector_controller.h` disposition=`merge` rank=`22` total_score=`65.91` risk=`HIGH`
- `tools/coredata_compile/coredata_emit_tlv.h` disposition=`merge` rank=`23` total_score=`65.89` risk=`HIGH`
- `tools/mod_builder/dom_mod_builder_controller.h` disposition=`merge` rank=`24` total_score=`65.26` risk=`HIGH`
- `tools/universe_editor/ue_commands.h` disposition=`merge` rank=`25` total_score=`64.74` risk=`HIGH`
- `tools/replay_analyzer/ra_diff.h` disposition=`merge` rank=`26` total_score=`64.44` risk=`HIGH`
- `tools/replay_viewer/dom_replay_viewer_controller.h` disposition=`merge` rank=`27` total_score=`64.2` risk=`HIGH`
- `tools/net_inspector/dom_net_inspector_controller.h` disposition=`merge` rank=`28` total_score=`64.07` risk=`HIGH`
- `tools/replay_analyzer/ra_parser.h` disposition=`merge` rank=`29` total_score=`63.32` risk=`HIGH`
- `tools/validator/validator_checks.cpp` disposition=`merge` rank=`30` total_score=`61.83` risk=`HIGH`
- `tools/coredata_compile/coredata_emit_tlv.cpp` disposition=`merge` rank=`31` total_score=`61.81` risk=`HIGH`
- `tools/validation/validator_reports.cpp` disposition=`merge` rank=`32` total_score=`61.7` risk=`HIGH`
- `tools/replay_analyzer/ra_parser.cpp` disposition=`merge` rank=`33` total_score=`60.74` risk=`HIGH`
- `tools/universe_editor/ue_queries.h` disposition=`merge` rank=`34` total_score=`60.26` risk=`HIGH`
- `tools/validation/validators_registry.cpp` disposition=`merge` rank=`35` total_score=`60.26` risk=`HIGH`
- `tools/world_editor/dom_world_editor_controller.h` disposition=`merge` rank=`36` total_score=`60.26` risk=`HIGH`
- `tools/replay_analyzer/ra_diff.cpp` disposition=`merge` rank=`37` total_score=`59.91` risk=`HIGH`
- `tools/universe_editor/ue_queries.cpp` disposition=`merge` rank=`38` total_score=`59.3` risk=`HIGH`
- `tools/replay_viewer/dom_replay_viewer_controller.cpp` disposition=`merge` rank=`39` total_score=`58.83` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_checks.cpp` disposition=`merge` rank=`40` total_score=`58.7` risk=`HIGH`
- `tools/universe_editor/ue_commands.cpp` disposition=`merge` rank=`41` total_score=`57.88` risk=`HIGH`
- `tools/net_inspector/dom_net_inspector_controller.cpp` disposition=`merge` rank=`42` total_score=`57.87` risk=`HIGH`
- `tools/world_editor/dom_world_editor_controller.cpp` disposition=`merge` rank=`43` total_score=`57.87` risk=`HIGH`
- `tools/save_inspector/dom_save_inspector_controller.cpp` disposition=`merge` rank=`44` total_score=`55.16` risk=`HIGH`
- `tools/mod_builder/dom_mod_builder_controller.cpp` disposition=`merge` rank=`45` total_score=`53.23` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/CLI_REFERENCE.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/DOC_INDEX.md, docs/audit/REPO_TREE_INDEX.md, docs/audit/SHIM_COVERAGE_REPORT.md, docs/audit/STABILITY_TAGGING_FINAL.md, docs/ci/CI_ENFORCEMENT_MATRIX.md, docs/ci/HYGIENE_QUEUE.md`

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
