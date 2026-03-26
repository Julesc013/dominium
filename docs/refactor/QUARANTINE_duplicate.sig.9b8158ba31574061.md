Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9b8158ba31574061`

- Symbol: `print_usage`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/mod_builder/main_mod_builder.cpp`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `rewire, deprecate, quarantine`

## Competing Files

- `tools/blueprint_editor/main_blueprint_editor.cpp`
- `tools/item_editor/main_item_editor.cpp`
- `tools/mod_builder/main_mod_builder.cpp`
- `tools/net_inspector/main_net_inspector.cpp`
- `tools/pack_editor/main_pack_editor.cpp`
- `tools/policy_editor/main_policy_editor.cpp`
- `tools/process_editor/main_process_editor.cpp`
- `tools/replay_viewer/main_replay_viewer.cpp`
- `tools/save_inspector/main_save_inspector.cpp`
- `tools/struct_editor/main_struct_editor.cpp`
- `tools/tech_editor/main_tech_editor.cpp`
- `tools/transport_editor/main_transport_editor.cpp`
- `tools/world_editor/main_world_editor.cpp`

## Scorecard

- `tools/mod_builder/main_mod_builder.cpp` disposition=`canonical` rank=`1` total_score=`69.29` risk=`HIGH`
- `tools/policy_editor/main_policy_editor.cpp` disposition=`quarantine` rank=`2` total_score=`67.26` risk=`HIGH`
- `tools/save_inspector/main_save_inspector.cpp` disposition=`drop` rank=`3` total_score=`66.39` risk=`HIGH`
- `tools/net_inspector/main_net_inspector.cpp` disposition=`drop` rank=`4` total_score=`60.61` risk=`HIGH`
- `tools/replay_viewer/main_replay_viewer.cpp` disposition=`drop` rank=`5` total_score=`59.79` risk=`HIGH`
- `tools/process_editor/main_process_editor.cpp` disposition=`drop` rank=`6` total_score=`57.76` risk=`HIGH`
- `tools/world_editor/main_world_editor.cpp` disposition=`drop` rank=`7` total_score=`57.63` risk=`HIGH`
- `tools/item_editor/main_item_editor.cpp` disposition=`drop` rank=`8` total_score=`57.54` risk=`HIGH`
- `tools/struct_editor/main_struct_editor.cpp` disposition=`drop` rank=`9` total_score=`57.54` risk=`HIGH`
- `tools/blueprint_editor/main_blueprint_editor.cpp` disposition=`drop` rank=`10` total_score=`55.61` risk=`HIGH`
- `tools/pack_editor/main_pack_editor.cpp` disposition=`drop` rank=`11` total_score=`54.64` risk=`HIGH`
- `tools/tech_editor/main_tech_editor.cpp` disposition=`drop` rank=`12` total_score=`54.64` risk=`HIGH`
- `tools/transport_editor/main_transport_editor.cpp` disposition=`drop` rank=`13` total_score=`54.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/REPORT_GAME_ARCH_DECISIONS.md, docs/audit/ARCHITECTURE_HEALTH.md, docs/audit/BR0_COMPLETION_REPORT.md, docs/audit/PROMPT_G_REPORT.md, docs/audit/REPO_TREE_INDEX.md, docs/ci/HYGIENE_QUEUE.md, docs/specs/DATA_FORMATS.md`

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

- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
