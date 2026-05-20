Status: DERIVED
Last Reviewed: 2026-05-19
Supersedes: none
Superseded By: none

# CANON_DEBT_CLEANUP_03

Task: REPOX-TESTX-CANON-PATHS-01
Started: 2026-05-19
Starting Branch: main
Starting Commit: be6f748a1e5812a8c71911bf4e1fd8099cc477a0

## Scope

Repair post-canonical-spine proof expectations without introducing new structure moves:

- Update active TestX survival/profile expectations from retired `data/registries` paths to `contracts/registry`.
- Update active client command/session test expectations from retired `apps/client/core` and `client/core` paths to `apps/client/command` and `apps/client/session`.
- Update RepoX active path expectations that still point at retired client command locations.
- Make RepoX failure output safe on Windows consoles so Unicode diagnostic output does not crash while printing violations.

## Non-Goals

- No broad content pack restructuring.
- No broad tools or docs fold.
- No schema taxonomy expansion beyond paths required by the proof lane.
- No archive/generated or archive/legacy evidence deletion.
- No recreation of `data/registries`.

## Before

- Branch `main` matched `origin/main`.
- HEAD was `be6f748a1e5812a8c71911bf4e1fd8099cc477a0`.
- Focused TestX survival/profile lane failed 10/10 because tests expected `data/registries/law_profiles.json`.
- RepoX had stale active client path expectations under `apps/apps/client/session/...` and raw `print()` failure output that could crash on Windows encoding.

## Routes

- Registry authority: `data/registries/*.json` -> `contracts/registry/*.json`.
- Client command bridge/registry: `apps/client/core/*` and `client/core/*` -> `apps/client/command/*`.
- Client session pipeline/refusal code files: `client/core/*` -> `apps/client/session/*`.
- RepoX presentation matrix schema: `contracts/schemas/governance/presentation_matrix.schema` -> `contracts/schema/governance/presentation_matrix.schema`.

## Validation Log

- `py -3 .aide/scripts/aide_lite.py validate`: PASS with existing warnings for the missing review decision policy ref and stale repo map source snapshot hash.
- Focused TestX survival/profile lane before: FAIL 10/10.
- Focused TestX survival/profile lane after path repair: PASS 10/10.
- `py -3 -m py_compile scripts/ci/check_repox_rules.py tools/xstack/repox/check.py`: PASS with pre-existing `tools/xstack/repox/check.py` invalid escape `SyntaxWarning`.
- `ctest --preset verify -R "(build_include_sanity|build_abi_boundaries)" --output-on-failure --timeout 300`: PASS 2/2.
- `ctest --preset verify -L smoke --output-on-failure --timeout 300`: PASS 57/57.
- `git diff --check`: PASS.
- RepoX after repair: FAILS with current-layout/governance blockers, but no Windows encoding crash and no broad pre-canon crash path.

## Remaining Debt

- RepoX still reports real current-layout governance violations after stale path repair; those remain visible rather than hidden.
- Remaining RepoX categories include doc status header debt, generated `dist/*` proof artifact expectations, process pack source-definition debt, identity/worldgen hash drift, pack compatibility proof debt, and semantic marker gaps.
- Broader `data/registries` references remain in unrelated invariant tests and generated/session tooling and need their own focused proof task if they block later lanes.
- Content pack layout, schema second-pass cleanup, tools fold, docs fold, and AIDE archive scan boundaries remain out of scope for this proof repair.
