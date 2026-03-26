Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b2a0a3b6857bc6b2`

- Symbol: `tools`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/validator/validator_checks.h`
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
- `tools/validator/validator_checks.cpp`
- `tools/validator/validator_checks.h`
- `tools/world_editor/dom_world_editor_controller.cpp`
- `tools/world_editor/dom_world_editor_controller.h`

## Scorecard

- `tools/validator/validator_checks.h` disposition=`canonical` rank=`1` total_score=`85.24` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_load.h` disposition=`quarantine` rank=`2` total_score=`75.89` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_report.h` disposition=`quarantine` rank=`3` total_score=`75.89` risk=`HIGH`
- `tools/coredata_compile/coredata_manifest.h` disposition=`merge` rank=`4` total_score=`75.48` risk=`HIGH`
- `tools/coredata_compile/coredata_load.h` disposition=`merge` rank=`5` total_score=`74.58` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_report.cpp` disposition=`merge` rank=`6` total_score=`74.12` risk=`HIGH`
- `tools/coredata_compile/coredata_validate.h` disposition=`drop` rank=`7` total_score=`73.55` risk=`HIGH`
- `tools/coredata_compile/coredata_load.cpp` disposition=`merge` rank=`8` total_score=`72.7` risk=`HIGH`
- `tools/coredata_compile/coredata_manifest.cpp` disposition=`drop` rank=`9` total_score=`71.63` risk=`HIGH`
- `tools/coredata_compile/coredata_validate.cpp` disposition=`drop` rank=`10` total_score=`71.24` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_load.cpp` disposition=`merge` rank=`11` total_score=`69.48` risk=`HIGH`
- `tools/validator/validator_checks.cpp` disposition=`merge` rank=`12` total_score=`68.52` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_checks.h` disposition=`drop` rank=`13` total_score=`67.06` risk=`HIGH`
- `tools/replay_analyzer/ra_parser.h` disposition=`drop` rank=`14` total_score=`66.67` risk=`HIGH`
- `tools/save_inspector/dom_save_inspector_controller.h` disposition=`merge` rank=`15` total_score=`65.91` risk=`HIGH`
- `tools/coredata_compile/coredata_emit_tlv.h` disposition=`drop` rank=`16` total_score=`65.89` risk=`HIGH`
- `tools/universe_editor/ue_commands.h` disposition=`drop` rank=`17` total_score=`65.7` risk=`HIGH`
- `tools/replay_analyzer/ra_diff.h` disposition=`drop` rank=`18` total_score=`65.63` risk=`HIGH`
- `tools/mod_builder/dom_mod_builder_controller.h` disposition=`merge` rank=`19` total_score=`65.26` risk=`HIGH`
- `tools/replay_viewer/dom_replay_viewer_controller.h` disposition=`merge` rank=`20` total_score=`64.2` risk=`HIGH`
- `tools/net_inspector/dom_net_inspector_controller.h` disposition=`merge` rank=`21` total_score=`64.07` risk=`HIGH`
- `tools/coredata_validate/coredata_validate_checks.cpp` disposition=`merge` rank=`22` total_score=`63.24` risk=`HIGH`
- `tools/replay_analyzer/ra_parser.cpp` disposition=`drop` rank=`23` total_score=`61.93` risk=`HIGH`
- `tools/universe_editor/ue_queries.h` disposition=`merge` rank=`24` total_score=`61.45` risk=`HIGH`
- `tools/universe_editor/ue_queries.cpp` disposition=`merge` rank=`25` total_score=`60.49` risk=`HIGH`
- `tools/world_editor/dom_world_editor_controller.h` disposition=`merge` rank=`26` total_score=`60.26` risk=`HIGH`
- `tools/replay_analyzer/ra_diff.cpp` disposition=`merge` rank=`27` total_score=`59.91` risk=`HIGH`
- `tools/universe_editor/ue_commands.cpp` disposition=`drop` rank=`28` total_score=`59.67` risk=`HIGH`
- `tools/coredata_compile/coredata_emit_tlv.cpp` disposition=`merge` rank=`29` total_score=`59.43` risk=`HIGH`
- `tools/replay_viewer/dom_replay_viewer_controller.cpp` disposition=`drop` rank=`30` total_score=`58.83` risk=`HIGH`
- `tools/net_inspector/dom_net_inspector_controller.cpp` disposition=`drop` rank=`31` total_score=`57.87` risk=`HIGH`
- `tools/world_editor/dom_world_editor_controller.cpp` disposition=`drop` rank=`32` total_score=`57.87` risk=`HIGH`
- `tools/save_inspector/dom_save_inspector_controller.cpp` disposition=`merge` rank=`33` total_score=`55.16` risk=`HIGH`
- `tools/mod_builder/dom_mod_builder_controller.cpp` disposition=`merge` rank=`34` total_score=`53.23` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/app/TESTX_INVENTORY.md, docs/architecture/INVARIANT_REGISTRY.md, docs/archive/ci/COREDATA_CONSISTENCY_REPORT.md, docs/archive/ci/PHASE1_AUDIT_REPORT.md, docs/audit/CODE_DATA_SEPARATION_REPORT.md, docs/audit/CONSISTENCY_AUDIT_REPORT.md, docs/audit/CONVERGENCE_FINAL.md, docs/audit/DOC_INDEX.md`

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
