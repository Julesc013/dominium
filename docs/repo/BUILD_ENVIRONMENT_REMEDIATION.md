# Build Environment Remediation

## Status

- Task ID: POST-CONVERGE-00
- Current build proof status: not proven locally
- Full build proven: no
- CTest proven: no

The source layout validators pass, but local configure/build/test proof is still blocked.

## CMake Verify Preset

`CMakePresets.json` defines the visible `verify` configure preset for Windows. It inherits:

`verify` -> `verify-win-vs2026` -> `msvc-base`

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

`cmake --list-presets` on this machine exposes only:

- `local`
- `verify`
- `release-check`
- `release-winnt-x86_64`

There are hidden or advanced Ninja/GCC/Clang presets in `CMakePresets.json`, including Linux and Windows clang-cl/MinGW lanes, but they are not visible default local Windows verify lanes. The visible `verify` lane is MSVC/Visual Studio 2022.

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
- `cmake --help`: lists `Visual Studio 17 2022` as a generator type
- `where.exe vswhere`: not found
- `where.exe cl`: not found
- `where.exe ninja`: not found

Classification: environment/preset design blocker. CMake supports the generator type, but no Visual Studio 2022 installation or compiler is discoverable. This is not enough evidence to call the repo code broken.

Recommended remediation options:

- install the required Visual Studio 2022 Build Tools locally
- document the verify preset environment requirement explicitly
- add a non-default Ninja fallback verify preset in a scoped build-remediation task
- use CI as authoritative MSVC verify proof if CI has Visual Studio 2022
- add a cross-platform smoke preset only after deciding its support tier in the component matrix

No preset or CMake semantics were changed in POST-CONVERGE-00.

## FAST Gate Failure

Command:

```text
python scripts/dev/gate.py verify --repo-root .
```

Result:

- exit code: 1
- primary failure class: `STRUCTURAL`
- runner: `repox_runner`
- failing command: `python scripts/ci/check_repox_rules.py --repo-root {repo_root} --profile {profile}`
- concrete exception: `ValueError: invalid mod policy registry`

The failure path is:

`check_worldgen_lock_required` -> `verify_worldgen_lock` -> `build_worldgen_lock_snapshot` -> `build_locked_identity_context` -> `build_pack_lock_payload` -> `_default_mod_policy_row`.

Focused diagnostic:

- `modding.load_mod_policy_registry('.')` returns schema validation errors.
- The key schema error is `unknown schema: mod_policy_profile`.
- `contracts/schemas/mod_policy_profile.schema.json` exists.
- `tools/xstack/compatx/schema_registry.py` still uses `SCHEMA_DIR_REL = "schemas"` and discovers root `schemas/`.
- Root `schemas/` no longer exists after CONVERGE-06.

Classification: likely stale-path fallout from schema convergence, surfaced by the FAST worldgen lock path. The smallest safe remediation is to update CompatX schema discovery to prefer `contracts/schemas/` and retain any necessary legacy fallback, then rerun mod policy registry validation and FAST.

## AIDE Pack Compatibility

Commands:

```text
python .aide/scripts/aide_lite.py doctor
python .aide/scripts/aide_lite.py validate
python .aide/scripts/aide_lite.py pack --task "POST-CONVERGE-00 health audit"
```

Results:

- doctor: pass
- validate: pass with existing warnings
- pack: fail

Failure:

```text
TypeError: write_text() got an unexpected keyword argument 'newline'
```

Environment:

- `python --version`: `Python 3.8.1`
- `pathlib.Path.write_text` signature: `(self, data, encoding=None, errors=None)`
- `py` launcher: not available

Likely fixes:

- require a newer Python for AIDE Lite pack generation
- patch AIDE Lite to write with `open(path, "w", encoding="utf-8", newline="\n")` for Python 3.8 compatibility
- consider both: document a Python floor and keep compatibility where low-risk

No AIDE code was changed in POST-CONVERGE-00.

## Recommended Build Remediation Sequence

1. Decide whether local `verify` is intentionally Windows/MSVC-only.
2. Fix or document the Visual Studio 2022 generator requirement.
3. Fix FAST `repox_runner` schema discovery / mod policy validation.
4. Fix or document AIDE pack Python compatibility.
5. Rerun `cmake --preset verify`.
6. If configure passes, run `cmake --build --preset verify` and `ctest --preset verify`.
7. Proceed to canonical local runtime/playtest proof only after build and FAST blockers are resolved or explicitly waived.
