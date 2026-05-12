# Build Environment Remediation

## Status

- Task ID: POST-CONVERGE-06
- Current build proof status: blocked locally
- Full build proven: no
- CTest proven: no
- FAST status: partial, structural blocker fixed, RepoX drift remains
- AIDE pack status: pass

The strict source layout validators remain the repo-level proof floor, but local configure/build/test proof is still blocked by the missing Visual Studio 2022 toolchain.

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

## Local Failure

Command:

```text
cmake --preset verify
```

Result:

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

Classification: environment-only `missing_generator`. CMake supports the generator type, but no Visual Studio 2022 installation or usable fallback compiler is discoverable.

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

1. Install Visual Studio 2022 Build Tools or run the canonical verify lane in CI with Visual Studio 2022.
2. Rerun `cmake --preset verify`.
3. If configure passes, run `cmake --build --preset verify` and `ctest --preset verify`.
4. Run a targeted RepoX drift remediation task to separate stale paths, generated evidence gaps, missing dist artifacts, and real invariant failures.
5. Proceed to POST-CONVERGE-07 only after build proof exists and FAST drift is either fixed or explicitly accepted by review.
