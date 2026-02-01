Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# ARCH_BUILD_ENFORCEMENT — Build and Boundary Lockdown (ENF2)





Status: enforced


Version: 3





## Purpose


This document defines the enforced build graph and architectural boundaries.


All violations MUST fail at configure or build time and MUST be treated as merge-blocking.





## Target graph (authoritative)


```


domino_engine (engine/)


   ^


   |


dominium_game (game/)


   ^        ^


   |        |


client   server





launcher_core (launcher/) -> engine::domino + libs::contracts


setup_core (setup/)       -> libs::contracts


tools_shared (tools/)     -> libs::contracts


dominium-tools (tools/)   -> tools_shared


data_validate (tools/)    -> engine::domino


validate_all (tools/)     -> (no engine link)


```





## Include boundaries (hard rules)


- `engine/include/**` is the ONLY public engine API surface.


- `engine/modules/**` and `engine/render/**` are internal and FORBIDDEN outside `engine/`.


- `game/` MUST NOT include from `engine/modules/**` or platform headers (ARCH-INC-001).


- `client/`, `server/`, `tools/` MUST NOT include from `engine/modules/**` (ARCH-INC-002).


- No `include_directories()` or `link_directories()` usage is allowed anywhere (BUILD-GLOBAL-001).





## CMake enforcement (configure/build failures)


Enforcement is done via target-scoped includes and configure-time assertions:


- `domino_engine` exposes only `engine/include/` as PUBLIC include directories.


- `dominium_game` links only `domino_engine` and MUST NOT link launcher/setup/libs targets.


- `dominium_client` and `dominium_server` link only `domino_engine` + `dominium_game`.


- Configure-time boundary checks fail if:


  - `domino_engine` exposes any public include outside `engine/include/`.


  - `domino_engine` links to forbidden top-level targets (ARCH-DEP-001).


  - `dominium_game` links to launcher/setup/libs targets (ARCH-DEP-002).





## How violations fail


- **Configure-time**: target graph assertions and include boundary checks (ARCH-DEP-001/002).


- **Build-time**: illegal includes fail compilation due to missing include paths (ARCH-INC-001/002).


- **Static checks**: `tools/ci/arch_checks.py` enforces repo-wide guards (ARCH-TOP-001, ARCH-RENDER-001, UI-BYPASS-001, EPIS-*).


- **Data validation**: `data_validate` and `engine_data_validate` validate data invariants (see `docs/guides/DATA_VALIDATION_GUIDE.md`).


- **Governance validation**: `tools/validation/validate_all` validates schema governance and policy enforcement.





## How to run architecture checks locally


```


python tools/ci/arch_checks.py --repo-root .


cmake --build <build-dir> --target check_arch


```


Use `--strict` to treat warnings as errors when applicable.





## How to run data validation locally


```


data_validate --input=<path> --schema-id=<u64> --schema-version=MAJOR.MINOR.PATCH


ctest -R engine_data_validate


```





## How to run governance validation locally


```


cmake --build <build-dir> --target validate_all


<build-dir>\\bin\\validate_all --repo-root=.


```





## CI command (noninteractive)


```


python tools/ci/arch_checks.py --repo-root .


<build-dir>\\bin\\validate_all --repo-root=. --strict=1


```





## Data validation command (noninteractive)


```


data_validate --input=<path> --schema-id=<u64> --schema-version=MAJOR.MINOR.PATCH


```





## Common errors and fixes


- **Error**: include of `engine/modules/**` from game/client/server/tools fails.


  - **Fix**: move the include to a public header under `engine/include/**` or use the public API.


- **Error**: platform headers included from game code.


  - **Fix**: move platform interactions into engine or client; use engine public APIs.


- **Error**: `domino_engine` exposes non-public include directories.


  - **Fix**: remove public include paths and keep internal paths PRIVATE.


- **Error**: `dominium_game` links to launcher/setup/libs targets.


  - **Fix**: remove the dependency and route through `domino_engine` public interfaces.


- **Error**: renderer backend token detected outside `engine/render/**` (ARCH-RENDER-001).


  - **Fix**: move backend code into `engine/render/**`.


- **Error**: top-level `source/` or `src/` directories found (ARCH-TOP-001).


  - **Fix**: remove or relocate into canonical top-level domains.


- **Error**: UI code directly queries sim/world state (UI-BYPASS-001).


  - **Fix**: route through EIL/capability snapshot interfaces.


- **Error**: UI includes authoritative headers or calls sim/world APIs (EPIS-*).


  - **Fix**: use `dominium/epistemic.h` and capability snapshots only.


- **Error**: `include_directories()` or `link_directories()` used in any CMake file (BUILD-GLOBAL-001).


  - **Fix**: replace with `target_include_directories()` on specific targets.





## Local verification (recommended)


```


python scripts/verify_includes_sanity.py


python scripts/verify_cmake_no_global_includes.py


python tools/ci/arch_checks.py --repo-root .


cmake -S . -B <build-dir>


cmake --build <build-dir>


ctest --test-dir <build-dir>


<build-dir>\\bin\\validate_all --repo-root=.


```





## See also


- `docs/architecture/ARCH_ENFORCEMENT.md`


- `docs/architecture/CANONICAL_SYSTEM_MAP.md`
