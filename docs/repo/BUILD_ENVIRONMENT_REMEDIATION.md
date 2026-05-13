# Build Environment Remediation

## Status

- Task ID: POST-CONVERGE-10D
- Current build proof status: build passes; CTest blocked
- Full build proven: yes
- CTest proven: no
- FAST status: partial, structural blocker fixed, RepoX drift remains
- AIDE pack status: pass

The strict source layout validators remain the repo-level proof floor. POST-CONVERGE-10 added a tuple build contract and machine probe. POST-CONVERGE-10B confirmed that Visual Studio 2022/MSVC v143 is detected. POST-CONVERGE-10C fixed the stale client/server CMake and test references. POST-CONVERGE-10D fixed the UI bind generated-output freshness blocker. Configure and build now pass for the VS2022/v143 tuple and canonical `verify` lane; CTest remains blocked in tools/auditx tests.

## CMake Verify Preset

`CMakePresets.json` defines the visible `verify` configure preset for Windows. It inherits:

```text
verify -> verify-win-vs2026 -> msvc-base
```

Current verify lane summary:

- generator: `Visual Studio 17 2022`
- architecture: `x64`
- binary dir: `${sourceDir}/out/build/vs2026/${presetName}`
- build mode: `Debug`
- tests: `DOM_BUILD_TESTS=ON`
- tools/setup/launcher/game: enabled
- C language: C89, required, no extensions
- C++ language: C++98, required, no extensions
- platform/backend defaults from `msvc-base`: `DOM_PLATFORM=sdl2`, `DOM_BACKEND_SDL2=ON`, `DOM_BACKEND_DX9=ON`, `DOM_BACKEND_GL2=ON`
- SDL2 root: `${sourceDir}/external/SDL2`
- downloads: `DOM_DISALLOW_DOWNLOADS=OFF`

`cmake --list-presets` on this machine exposes:

- `local`
- `verify`
- `release-check`
- `release-winnt-x86_64`

## Local Build History

Original POST-CONVERGE-06 command:

```text
cmake --preset verify
```

Original result:

```text
CMake Error at CMakeLists.txt:6 (project):
  Generator

    Visual Studio 17 2022

  could not find any instance of Visual Studio.
```

Local tool evidence:

- `cmake --version`: `4.2.0`
- `cmake --help`: lists `Visual Studio 17 2022`
- `where.exe vswhere`: not found
- `where.exe cl`: not found
- `where.exe ninja`: not found
- `where.exe gcc`, `clang`, `clang-cl`, `mingw32-make`, `nmake`, and `make`: not found

POST-CONVERGE-10 classification: environment-only `missing_generator`.

POST-CONVERGE-10B updated classification: `path_stale_after_convergence`.

POST-CONVERGE-10C updated classification: `generated_output_stale`. The missing Visual Studio blocker and stale client/server path blocker are resolved on this machine, but build now fails because `tool_ui_bind --check` reports stale generated outputs in `libs/appcore/ui_bind/`.

POST-CONVERGE-10D updated classification: `test_failure` and `long_running_or_timeout`. The UI bind freshness blocker is resolved by pinning tracked UI bind generated sources to LF line endings. Tuple and canonical builds pass. CTest times out in tools/auditx tests after failures including `tools_coverage_inspect` missing `compat`, auditx/governance model paths assuming root `schema`, and the existing RepoX drift backlog.

Current build result:

```text
python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --build
cmake --build --preset verify
```

Both commands pass on this machine after POST-CONVERGE-10D. CTest remains blocked.

## POST-CONVERGE-10 Build Contract Probe

New build contract and local tooling:

- `contracts/build/floors.toml`
- `contracts/build/toolchains.toml`
- `contracts/build/tuples.toml`
- `contracts/build/artifacts.toml`
- `tools/build/probe_toolchains.py`
- `tools/build/generate_user_presets.py`
- `tools/build/validate_build_contract.py`
- `tools/build/run_tuple.py`

POST-CONVERGE-10B probe result:

- CMake: `4.2.0`
- Python: `3.8.1`
- Visual Studio 17 2022: detected, Visual Studio Enterprise 2022 `17.14.37301.10`
- MSVC v143: detected by CMake as MSVC tools `14.44.35207`
- Windows SDK: detected by CMake as `10.0.26100.0`
- Visual Studio 18 2026: not detected
- Visual Studio 15 2017: not detected
- Visual Studio 2015: legacy VS14 paths detected, not used as canonical proof lane
- Ninja: not detected
- GCC/G++: not detected
- Clang/Clang++/clang-cl: not detected
- generated local presets: `.dominium.local/CMakeUserPresets.generated.json` and ignored `CMakeUserPresets.json`
- generated tuple presets: `verify.winnt10.x64.msvc143.mt.debug`, `verify.host.host.host_default.host.debug`, `smoke.host.host.host_default.host.debug`

Generated local presets expose the canonical VS2022 tuple. POST-CONVERGE-10C remediated stale CMake/test references:

- `client/presentation/frame_graph_builder.cpp` should now be represented from `apps/client/presentation/frame_graph_builder.cpp`.
- `server/authority/dom_server_authority.cpp` should now be represented from `apps/server/authority/dom_server_authority.cpp`.

Resolved UI bind blocker:

- `libs/appcore/ui_bind/ui_command_binding_table.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_localisation_usage_report.json`

These tracked generated outputs are now protected by `.gitattributes`:

```text
libs/appcore/ui_bind/** text eol=lf
```

POST-CONVERGE-06 remediation:

- no preset or CMake semantics changed
- no fallback preset added because it could not be validated locally
- build verification path documented in `docs/repo/BUILD_VERIFICATION_PATHS.md`

## FAST Gate Failure

Command:

```text
python scripts/dev/gate.py verify --repo-root .
```

Initial POST-CONVERGE-06 result:

- exit code: 1
- primary failure class: `STRUCTURAL`
- runner: `repox_runner`
- concrete exception: `ValueError: invalid mod policy registry`

Initial failure path:

`check_worldgen_lock_required` -> `verify_worldgen_lock` -> `build_worldgen_lock_snapshot` -> `build_locked_identity_context` -> `build_pack_lock_payload` -> `_default_mod_policy_row`.

Root cause:

- `modding.load_mod_policy_registry('.')` returned schema validation errors.
- The key schema error was `unknown schema: mod_policy_profile`.
- `contracts/schemas/mod_policy_profile.schema.json` existed.
- `tools/xstack/compatx/schema_registry.py` still discovered root `schemas/`.
- Root `schemas/` no longer exists after convergence.

POST-CONVERGE-06 remediation:

- `tools/xstack/compatx/schema_registry.py` now prefers `contracts/schemas/` and keeps `schemas/` as a legacy fallback.
- `game/domains/worldgen/mw/mw_surface_refiner_l3.py` now imports the Earth surface generator from `game.domains.worldgen.earth`.
- `scripts/ci/check_repox_rules.py` now points worldgen source constants at the canonical `game/domains/...` paths.

Focused result after remediation:

- `modding.load_mod_policy_registry('.')`: pass
- loaded policy IDs: `mod_policy.anarchy`, `mod_policy.lab`, `mod_policy.strict`
- XStack FAST now reaches RepoX drift reporting and fails with primary failure class `DRIFT`
- direct RepoX profile records 5 warnings and 1800 failures

Remaining FAST classification: broad RepoX drift backlog. This includes stale canonical-doc index entries, missing generated distribution descriptors, stale AppShell/embodiment/geo path assumptions, generated audit drift, rule-map gaps, and root-structure drift. This is outside the safe scope of POST-CONVERGE-06.

## AIDE Pack Compatibility

Commands:

```text
python .aide/scripts/aide_lite.py doctor
python .aide/scripts/aide_lite.py validate
python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-06 build and gate remediation"
```

Before remediation:

- doctor: pass
- validate: pass with existing warnings
- pack: fail with `TypeError: write_text() got an unexpected keyword argument 'newline'`

Environment:

- `python --version`: `Python 3.8.1`
- `pathlib.Path.write_text` signature: `(self, data, encoding=None, errors=None)`
- `py` launcher: not available

POST-CONVERGE-06 remediation:

- `.aide/scripts/aide_lite.py` now writes through `path.open("w", encoding="utf-8", newline="\n")`.
- AIDE pack now passes and updates `.aide/context/latest-task-packet.md`.

## Recommended Build Remediation Sequence

1. Run targeted CTest/auditx remediation for the current tools/auditx failures and timeout.
2. Rerun `python tools/build/run_tuple.py --repo-root . --tuple verify.winnt10.x64.msvc143.mt.debug --test`.
3. Rerun `ctest --preset verify`.
4. Run a targeted RepoX drift remediation task to separate stale paths, generated evidence gaps, missing dist artifacts, and real invariant failures.
5. Proceed to product boot proof after CTest is green or explicitly accepted as warning-only for POST-CONVERGE-11.
