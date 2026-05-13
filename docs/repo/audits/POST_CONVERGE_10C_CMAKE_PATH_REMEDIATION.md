# POST-CONVERGE-10C CMake Path Remediation Audit

## Status

- Task ID: POST-CONVERGE-10C
- Result: partial
- Date/time: 2026-05-13T18:04:43+10:00
- Branch: `main`
- HEAD SHA: `2aed29926182de61d9f5e20c8c6362b888f5152d`
- origin/main SHA: `2aed29926182de61d9f5e20c8c6362b888f5152d`
- Working tree status before task: clean tracked tree; ignored `.dominium.local/`, `dist/docs/`, and `dist/sys/` present
- Working tree status after task: CMake/test path remediation, build proof docs, and audit committed; generated local outputs remain ignored/uncommitted

## Scope

This task covered:

- targeted stale CMake/build path remediation
- no feature work
- no runtime proof
- no product boot proof
- no package/projection proof
- no renderer/platform/native implementation
- no product ID or executable rename

## Prior Blocker

POST-CONVERGE-10B recorded these CMake generation blockers:

| Stale Reference | Correct Source |
| --- | --- |
| `client/presentation/frame_graph_builder.cpp` | `apps/client/presentation/frame_graph_builder.cpp` |
| `server/authority/dom_server_authority.cpp` | `apps/server/authority/dom_server_authority.cpp` |

This task also found active related references to:

- `client/presentation/render_prep_system.cpp`
- `client/presentation` include directory
- `server/authority/dom_server_authority.h`
- `client/core/client_command_bridge.c`
- `client/core/client_commands_registry.c`

Those related references were only updated where they were active CMake, CTest, TestX, or RepoX rule inputs.

## References Found

| Reference | File | Classification | Action | Notes |
| --- | --- | --- | --- | --- |
| `client/presentation/frame_graph_builder.cpp` | `engine/tests/CMakeLists.txt` | active CMake test source list | updated | now `apps/client/presentation/frame_graph_builder.cpp` |
| `client/presentation/render_prep_system.cpp` | `engine/tests/CMakeLists.txt` | active CMake test source list | updated | same moved presentation root |
| `client/presentation` | `engine/tests/CMakeLists.txt` | active CMake test include dir | updated | now `apps/client/presentation` |
| `server/authority/dom_server_authority.cpp` | `tests/authority/CMakeLists.txt` | active CMake test source list | updated | now `apps/server/authority/dom_server_authority.cpp` |
| `server/authority/dom_server_authority.cpp` | `tests/tourist/CMakeLists.txt` | active CMake test source list | updated | now `apps/server/authority/dom_server_authority.cpp` |
| `server/authority/dom_server_authority.cpp` | `tests/services/CMakeLists.txt` | active CMake test source list | updated | now `apps/server/authority/dom_server_authority.cpp` |
| `server/authority/dom_server_authority.cpp` | `tests/piracy_containment/CMakeLists.txt` | active CMake test source list | updated | now `apps/server/authority/dom_server_authority.cpp` |
| `server/authority/dom_server_authority.h` | authority/tourist/services/piracy C++ tests | active test include | updated | include now targets `apps/server/authority/dom_server_authority.h` |
| `server/authority/dom_server_authority.*` | `tests/invariant/*.py` | active TestX path input | updated | now `apps/server/authority/...` |
| `client/core/client_command_bridge.c` | `tests/invariant/*.py` | active TestX path input | updated | now `apps/client/core/client_command_bridge.c` |
| `client/core/client_command_bridge.c` and `client/core/client_commands_registry.c` | `repo/repox/rulesets/core.json` | active RepoX rule scope input | updated | now `apps/client/core/...` |

Historical audit data and generated evidence references were not rewritten.

## Changes Made

| File | Change | Reason | Semantics Changed? |
| --- | --- | --- | --- |
| `engine/tests/CMakeLists.txt` | rewired render prep test source/include paths to `apps/client/presentation` | fix moved client presentation sources | no |
| `tests/authority/CMakeLists.txt` | rewired authority implementation source to `apps/server/authority` | fix moved server authority source | no |
| `tests/tourist/CMakeLists.txt` | rewired authority implementation source to `apps/server/authority` | fix moved server authority source | no |
| `tests/services/CMakeLists.txt` | rewired authority implementation source to `apps/server/authority` | fix moved server authority source | no |
| `tests/piracy_containment/CMakeLists.txt` | rewired authority implementation source to `apps/server/authority` | fix moved server authority source | no |
| authority/tourist/services/piracy C++ tests | rewired authority header include to `apps/server/authority` | preserve active test compile path | no |
| `tests/invariant/*.py` | rewired client/server path constants to `apps/...` | preserve active TestX path checks | no |
| `repo/repox/rulesets/core.json` | rewired client/server scope paths to `apps/...` | keep active RepoX scope paths current | no |

## Configure / Build / Test Result

| Command | Result | Notes |
| --- | --- | --- |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run` | pass | tuple commands resolved |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure` | pass | known stale CMake path blocker cleared |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build` | fail | build progressed and produced product binaries, then failed at `ui_bind_phase` |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test` | not run | build failed |
| `cmake --preset verify` | pass | canonical verify configure now generates build files |
| `cmake --build --preset verify` | fail | same UI binding freshness blocker; bounded smoke target also reports `tool_ui_bind.check` failure |
| `ctest --preset verify` | not run | build failed |

New blocker classification: `generated_output_stale`.

Primary build errors:

- `UI_BIND_ERROR|output|stale|libs/appcore/ui_bind/ui_command_binding_table.h`
- `UI_BIND_ERROR|output|stale|libs/appcore/ui_bind/ui_command_binding_table.c`
- `UI_BIND_ERROR|output|stale|libs/appcore/ui_bind/ui_accessibility_map.h`
- `UI_BIND_ERROR|output|stale|libs/appcore/ui_bind/ui_accessibility_map.c`
- `UI_BIND_ERROR|output|stale|libs/appcore/ui_bind/ui_localisation_usage_report.json`

## Native Binary Result

| Product | Produced? | Path | Notes |
| --- | --- | --- | --- |
| setup | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/setup.exe` | binary produced before build gate failure |
| launcher | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/launcher.exe` | binary produced before build gate failure |
| client | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/client.exe` | binary produced before build gate failure |
| server | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/server.exe` | binary produced before build gate failure |
| tools | yes | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/tools.exe` | binary produced before build gate failure |

The canonical `verify` build also produced `setup.exe`, `launcher.exe`, `client.exe`, and `server.exe` under `out/build/vs2026/verify/bin` before failing. Generated binaries were not committed.

## Remaining Blockers

- Build remains red because UI bind generated outputs are stale.
- `ctest --preset verify` was not run because both tuple and canonical builds failed.
- Generated native binaries exist locally, but they are not accepted as fully build-proven until the build gate passes.

## Files Added/Changed

- Added `docs/repo/audits/POST_CONVERGE_10C_CMAKE_PATH_REMEDIATION.md`.
- Updated active CMake/test references under `engine/tests/`, `tests/authority/`, `tests/tourist/`, `tests/services/`, `tests/piracy_containment/`, `tests/invariant/`, and `repo/repox/rulesets/core.json`.
- Updated POST-CONVERGE-10/10B build proof docs, build verification docs, native binary proof, and next steps.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | pass | clean tracked tree before task; later task edits staged for commit |
| `git rev-parse HEAD` | pass | `2aed29926182de61d9f5e20c8c6362b888f5152d` |
| `git rev-parse origin/main` | pass | `2aed29926182de61d9f5e20c8c6362b888f5152d` |
| `python .aide/scripts/aide_lite.py doctor` | pass | existing optional artifact warnings only |
| `python .aide/scripts/aide_lite.py validate` | pass | existing review packet warnings |
| `python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-10C CMake path remediation"` | pass | task packet updated |
| `rg` stale client/server path search | pass | active stale references found and remediated |
| `python -m py_compile tools/build/build_contract_common.py tools/build/probe_toolchains.py tools/build/generate_user_presets.py tools/build/validate_build_contract.py tools/build/run_tuple.py` | pass | shell emitted unrelated oh-my-posh transient access message |
| `python tools/build/validate_build_contract.py --repo-root . --strict` | pass | build contract valid |
| `python tools/build/probe_toolchains.py --repo-root . --out .dominium.local/toolchains.detected.json` | pass | available: `host_default`, `msvc143` |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out .dominium.local/CMakeUserPresets.generated.json` | pass | generated 3 tuple presets |
| `python tools/build/generate_user_presets.py --repo-root . --probe .dominium.local/toolchains.detected.json --out CMakeUserPresets.json --force` | pass | temporary ignored file generated for CMake, removed before final strict validation |
| `cmake --list-presets=all` | pass | generated tuple presets visible while `CMakeUserPresets.json` existed |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --dry-run` | pass | tuple commands resolved |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --configure` | pass | CMake generation succeeds |
| `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build` | fail | build fails at `ui_bind_phase` stale generated-output check |
| `cmake --preset verify` | pass | canonical verify configure succeeds |
| `cmake --build --preset verify` | fail | build fails at bounded smoke/UI bind stale generated-output checks |
| `ctest --preset verify` | not run | build failed |
| `python tools/validators/check_repo_layout.py --repo-root . --strict` | pass | after removing root-level generated build surfaces |
| `python tools/validators/check_root_allowlist.py --repo-root . --strict` | pass | after removing root-level generated build surfaces |
| `python tools/validators/check_distribution_layout.py --repo-root . --strict` | pass | warnings: none |
| `python tools/validators/check_component_matrices.py --repo-root . --strict` | pass | warnings: none |
| `python scripts/verify_docs_sanity.py --repo-root .` | pass | docs sanity OK |
| `python scripts/verify_build_target_boundaries.py --repo-root .` | pass | build boundary checks passed; shell emitted unrelated oh-my-posh transient access message |
| `python scripts/verify_ui_shell_purity.py --repo-root .` | pass | UI shell purity OK; shell emitted unrelated oh-my-posh transient access message |
| `python scripts/verify_abi_boundaries.py --repo-root .` | pass | ABI boundary check OK |
| `python tools/validators/check_local_playtest_path.py --repo-root .` | pass, blocked proof | validator still reports missing product binaries in its expected path |
| `python tools/validators/check_product_boot_matrix.py --repo-root .` | pass, partial proof | validator still reports missing product binaries in its expected path |
| `python tools/validators/check_portable_projection.py --repo-root .` | pass, partial proof | validator still reports missing binaries/projection root |
| `python -m json.tool repo/repox/rulesets/core.json` | pass | active ruleset JSON parses |
| `python -m py_compile tests/invariant/test_authority_context_enforcement.py tests/invariant/test_client_cannot_escalate_entitlements.py tests/invariant/test_server_rejects_capability_escalation.py` | pass | updated invariant tests parse |
| direct invariant scripts for authority context/escalation | pass | all three updated path checks pass |
| `git diff --check` | pass | CRLF conversion warnings only |
| `git diff --cached --check` | pass | CRLF conversion warnings only |

## Readiness

- ready_for_POST_CONVERGE_11: no
- reason: product binaries were produced, but the build is still failing on stale UI bind generated outputs, so native binary proof is not yet green.

## POST-CONVERGE-10D Follow-up

POST-CONVERGE-10D remediated the UI bind freshness blocker.

Updated result:

- `libs/appcore/ui_bind/**` is now pinned to LF line endings for byte-identical generated-source freshness checks.
- `tool_ui_bind --check`: pass.
- `verify.winnt10.x64.msvc143.mt.debug` configure/build: pass.
- `cmake --preset verify`: pass.
- `cmake --build --preset verify`: pass.
- Tuple and canonical CTest: timeout/fail in tools/auditx tests.
- Native product binaries are present under `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/`.

Current blocker: targeted CTest/auditx remediation is required before native build/test proof is fully green.
