# Module Quality Report

## Largest Source Or Tool Files

- tools/xstack/sessionx/process_runtime.py: 3258637 bytes (unknown)
- tools/xstack/repox/check.py: 1459109 bytes (unknown)
- .aide/scripts/aide_lite.py: 1379225 bytes (AIDE Lite)
- tools/xstack/registry_compile/compiler.py: 628932 bytes (unknown)
- scripts/ci/check_repox_rules.py: 601089 bytes (unknown)
- apps/client/shell/client_shell.c: 503238 bytes (unknown)
- game/domains/inspection/inspection_engine.py: 262860 bytes (unknown)
- apps/client/app/main_client.c: 249301 bytes (unknown)
- tools/ui_editor/ui_editor_main_win32.cpp: 206863 bytes (unknown)
- game/rules/scale/scale_collapse_expand.cpp: 195951 bytes (unknown)
- apps/client/interaction/inspection_overlays.py: 191921 bytes (unknown)
- tools/audit/arch_audit_common.py: 184504 bytes (unknown)
- tools/setup/setup_cli.py: 175984 bytes (unknown)
- tools/xstack/sessionx/runner.py: 164968 bytes (unknown)
- models/model_engine.py: 155570 bytes (unknown)
- net/srz/shard_coordinator.py: 131172 bytes (unknown)
- tools/tools_host_main.c: 130598 bytes (unknown)
- tools/migration/root_move_map.json: 126531 bytes (unknown)
- tools/launcher/launcher_cli.py: 119366 bytes (unknown)
- game/domains/thermal/network/thermal_network_engine.py: 114126 bytes (unknown)

## High Dependency Count Candidates

- .aide/scripts/aide_lite.py: large_module_candidate, missing_doc_candidate, mixed_purpose_candidate, orphan_candidate, public_surface_missing_doc_candidate, reuse_candidate
- tools/mvp/stress_gate_common.py: missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- tools/setup/setup_cli.py: large_module_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- tools/xstack/repox/check.py: large_module_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- tools/xstack/sessionx/process_runtime.py: large_module_candidate, missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner
- validation/validation_engine.py: missing_test_or_validator_candidate, mixed_purpose_candidate, orphan_candidate, reuse_candidate, unknown_owner

## Mixed Purpose Candidates

- .aide/scripts/aide_lite.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- apps/client/app/main_client.c: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- apps/client/interaction/inspection_overlays.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- apps/client/shell/client_shell.c: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- game/domains/fluids/network/fluid_network_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- game/domains/inspection/inspection_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- game/domains/processes/process_run_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- game/domains/thermal/network/thermal_network_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- game/rules/scale/scale_collapse_expand.cpp: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- models/model_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- net/policies/policy_server_authoritative.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- net/srz/shard_coordinator.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- scripts/ci/check_repox_rules.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/audit/arch_audit_common.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/launcher/launcher_cli.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/lib/lib_stress_common.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/migration/root_move_map.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/mvp/stress_gate_common.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/mvp/toolchain_matrix_common.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/review/xi5x2_common.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/setup/setup_cli.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/tools_host_main.c: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/ui_editor/ui_editor_main_win32.cpp: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/compatx/version_registry.json: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/registry_compile/compiler.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/repox/check.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/sessionx/observation.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/sessionx/process_runtime.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- tools/xstack/sessionx/runner.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.
- validation/validation_engine.py: Inspect references and owner before any future refactor; do not delete from Q38 evidence.

## Owner Summary

- AIDE Git workflow: 13
- AIDE Lite: 16
- AIDE changelog preview: 4
- AIDE context compiler: 13
- AIDE control plane: 78
- AIDE evals: 55
- AIDE governance: 21
- AIDE self-hosting queue: 39
- documentation reference: 4
- unknown: 15177

## Caveats

- module findings are first-pass candidates
- Q38 does not refactor or extract helpers
