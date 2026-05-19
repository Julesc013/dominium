Status: implemented with documented residual validator debt outside the docs taxonomy fold
Task: DOCS-CANON-01
Starting Commit: 2241a7d7a2c748178bae003659e7c8858d77f8e0
Branch: main

# DOCS-CANON-01 Audit

## Scope

This pass folds the active `docs/` tree into compact human-documentation
ownership categories. It routes old first-level roots, product/runtime mirrors,
domain-topic roots, stale refactor roots, generated evidence pockets, and
root-level loose documents into canonical documentation homes.

The pass does not redesign runtime, game, engine, schema, content, app,
Workbench, tools, or AIDE behavior. Active references were updated only where
they pointed at moved documentation paths.

## Preflight

- `git status --short`: clean
- `git rev-parse --abbrev-ref HEAD`: `main`
- `git rev-parse HEAD`: `2241a7d7a2c748178bae003659e7c8858d77f8e0`
- `py -3 .aide/scripts/aide_lite.py doctor`: PASS
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with pre-existing AIDE warnings about a missing review packet reference and stale repo-map snapshot hash.

## Roots Inspected

The active first-level docs roots were inspected with `git ls-files docs`.
Suspicious source mirrors and topic roots inspected included `accessibility`,
`agents`, `aide`, `audit`, `blueprint`, `ci`, `civilisation`, `client`,
`contracts`, `control`, `diegetics`, `electric`, `embodiment`, `epistemics`,
`examples`, `fields`, `gameplay`, `glossary`, `guides`, `impact`,
`infrastructure`, `interaction`, `interior`, `knowledge`, `launcher`, `lib`,
`logic`, `materials`, `mechanics`, `meta`, `mobility`, `mvp`, `omega`, `ops`,
`pack_format`, `packs`, `physical`, `player`, `policies`, `pollution`,
`post_canon`, `process`, `prompts`, `realities`, `reality`, `refactor`,
`repox`, `restructure`, `roadmap`, `scale`, `schema`, `server`, `settings`,
`setup`, `signals`, `sol`, `specs`, `system`, `time`, `universe`, `ux`,
`visualization`, and `xstack`.

## Canonical Roots

The resulting active `docs/` roots are:

- `docs/apps/`
- `docs/architecture/`
- `docs/archive/`
- `docs/build/`
- `docs/canon/`
- `docs/compatibility/`
- `docs/content/`
- `docs/development/`
- `docs/distribution/`
- `docs/domains/`
- `docs/engine/`
- `docs/game/`
- `docs/governance/`
- `docs/modding/`
- `docs/operations/`
- `docs/performance/`
- `docs/planning/`
- `docs/reference/`
- `docs/release/`
- `docs/repo/`
- `docs/runtime/`
- `docs/safety/`
- `docs/security/`
- `docs/testing/`

`docs/canon/` and `docs/planning/` are finite protected exceptions to the
target taxonomy. They remain because `AGENTS.md` and the repository authority
model bind to those exact paths as canonical doctrine and planning authority.
The docs taxonomy validator records and allows those two roots explicitly.

The only active files directly under `docs/` are `docs/README.md` and
`docs/.gitignore`.

## Classification Decisions

- Product docs moved to `docs/apps/<product>/`: `client`, `server`, `setup`,
  and `launcher`.
- Runtime-facing docs moved to `docs/runtime/<area>/`: accessibility, settings,
  UI/UX, render visualization, storage-oriented `lib`, and related runtime
  documentation.
- Domain docs moved to `docs/domains/<canonical-domain>/`: civilization,
  electricity, embodiment, fields, fluids, infrastructure, interiors,
  knowledge, logic, materials, mechanics, mobility, physics, pollution,
  processes, reality, scale, signals, astronomy/sol, and universe.
- Game-facing human doctrine moved to `docs/game/`: agents, diegetics,
  epistemics, gameplay, interaction, player, and realities.
- Repo/governance/development docs moved to `docs/repo/`,
  `docs/governance/`, or `docs/development/` based on current ownership.
- Pack and package-format prose moved to `docs/content/packs/` and
  `docs/distribution/package-format/`.
- Schema, contracts, examples, glossary, FAQ, philosophy, and prose specs moved
  to `docs/reference/` subtrees. Machine-readable contract authority was not
  promoted into docs by this task.
- Refactor, restructure, audit, prompt-slice, old status, and historical
  planning/evidence docs moved under `docs/archive/`.

## Moved Files And Directories

Directory moves used `git mv`. Major directory routes:

- `docs/accessibility/` -> `docs/runtime/ui/accessibility/`
- `docs/agents/` -> `docs/game/agents/`
- `docs/aide/` -> `docs/development/aide/`
- `docs/audit/` -> `docs/archive/audit/`
- `docs/blueprint/` -> `docs/archive/blueprint/`
- `docs/ci/` -> `docs/testing/ci/`
- `docs/civilisation/` -> `docs/domains/civilization/`
- `docs/client/` -> `docs/apps/client/`
- `docs/contracts/` -> `docs/reference/contracts/`
- `docs/control/` -> `docs/governance/control/`
- `docs/electric/` -> `docs/domains/electricity/`
- `docs/fields/` -> `docs/domains/fields/`
- `docs/launcher/` -> `docs/apps/launcher/`
- `docs/lib/` -> `docs/runtime/storage/`
- `docs/materials/` -> `docs/domains/materials/`
- `docs/mechanics/` -> `docs/domains/mechanics/`
- `docs/ops/` -> `docs/operations/`
- `docs/pack_format/` -> `docs/distribution/package-format/`
- `docs/packs/` -> `docs/content/packs/`
- `docs/physical/` -> `docs/domains/physics/physical/`
- `docs/process/` -> `docs/domains/processes/`
- `docs/refactor/` -> `docs/archive/refactor/`
- `docs/restructure/` -> `docs/archive/restructure/`
- `docs/schema/` -> `docs/reference/schema/`
- `docs/server/` -> `docs/apps/server/`
- `docs/setup/` -> `docs/apps/setup/`
- `docs/specs/` -> `docs/reference/specs/`
- `docs/system/` -> `docs/architecture/system/`
- `docs/time/` -> `docs/engine/time/`
- `docs/visualization/` -> `docs/runtime/render/visualization/`
- `docs/xstack/` -> `docs/development/xstack/`

Root-level document moves included:

- `docs/ARCHITECTURE.md` -> `docs/architecture/ROOT_ARCHITECTURE.md`
- `docs/CAPABILITY_STAGES.md` -> `docs/game/CAPABILITY_STAGES.md`
- `docs/CODE_CHANGE_JUSTIFICATION.md` -> `docs/development/CODE_CHANGE_JUSTIFICATION.md`
- `docs/CONTRIBUTING.md` -> `docs/development/CONTRIBUTING.md`
- `docs/FAQ.md` -> `docs/reference/FAQ.md`
- `docs/GLOSSARY.md` -> `docs/reference/GLOSSARY.md`
- `docs/MODDER_GUIDE.md` -> `docs/modding/MODDER_GUIDE.md`
- `docs/PHILOSOPHY.md` -> `docs/reference/PHILOSOPHY.md`
- `docs/PROCESS_REGISTRY.md` -> `docs/domains/processes/PROCESS_REGISTRY.md`
- `docs/SCHEMA_CANON_ALIGNMENT.md` -> `docs/reference/schema/SCHEMA_CANON_ALIGNMENT.md`
- `docs/SCHEMA_EVOLUTION.md` -> `docs/reference/schema/SCHEMA_EVOLUTION.md`
- `docs/STATUS_NOW.md` -> `docs/archive/STATUS_NOW.md`
- `docs/SURVIVAL_SLICE.md` -> `docs/archive/SURVIVAL_SLICE.md`
- `docs/TESTX_STAGE_MATRIX.md` -> `docs/testing/TESTX_STAGE_MATRIX.md`
- `docs/WHAT_PLAYERS_CAN_DO.md` -> `docs/game/player/WHAT_PLAYERS_CAN_DO.md`
- `docs/XSTACK.md` -> `docs/development/xstack/XSTACK.md`

## Reference Updates

Active references to moved docs paths were updated across repository prose,
scripts, CMake, registries, tests, and source comments/string paths. Historical
and generated snapshots were not treated as blockers.

Intentional old-path strings retained in active source are limited to:

- route alias tables in `scripts/ci/check_repox_rules.py`
- route alias tables in `tools/migration/canon_spine_new.py`
- negative fixtures in `tools/validators/repo/check_docs_taxonomy.py`

## Generated And Historical Material

Generated or historical documentation retained under docs was routed to
`docs/archive/` where it remains human-readable historical evidence. Generated
reports outside docs, including `.aide/**`, `archive/generated/**`,
`archive/legacy/**`, `external/**`, and broader `archive/**` material, were not
manually rewritten for this pass. A validator run briefly produced untracked
`docs/audit/**` outputs from old defaults; those generated files were removed
and the active `docs/audit` root remains absent.

## Validator Changes

Added `tools/validators/repo/check_docs_taxonomy.py` and wired it into
`tools/CMakeLists.txt` as:

- `dominium_docs_taxonomy_selftest`
- `dominium_docs_taxonomy`

The validator fails noncanonical first-level docs roots, allows canonical roots,
allows the finite `canon` and `planning` exceptions, and allows `docs/archive`
historical material.

## Validation Results

- `git diff --check`: PASS
- Changed JSON parse sweep with `python -m json.tool`: PASS, 456 changed JSON files parsed.
- `python tools/validators/repo/check_docs_taxonomy.py --self-test`: PASS
- `python tools/validators/repo/check_docs_taxonomy.py --repo-root . --strict`: PASS
- `python scripts/verify_docs_sanity.py --repo-root .`: PASS
- Stale active docs reference sweep: PASS except intentional route aliases in
  `scripts/ci/check_repox_rules.py`, `tools/migration/canon_spine_new.py`, and
  negative fixtures in `tools/validators/repo/check_docs_taxonomy.py`.
- `py -3 .aide/scripts/aide_lite.py validate`: PASS with warnings about a
  missing review packet reference and stale repo-map source snapshot hash.
- `python tools/validators/repo/check_tools_taxonomy.py --repo-root . --strict`: PASS.
- Bad-root validator: no standalone validator found at the checked repo paths.
- UI shell purity validator: PASS.
- ABI validator: no standalone validator found at the checked repo paths.
- `python scripts/ci/check_repox_rules.py --proof-manifest-out archive/generated/audit/DOCS_CANON_01_repox_proof_manifest.json --profile-out archive/generated/audit/DOCS_CANON_01_repox_profile.json`: FAIL with residual RepoX debt. Docs-canon fallout was repaired far enough for the command to complete with canonical output paths, but residual failures remain in pre-existing rule families such as duplicate logic pressure, `INV-CANON-NO-HIST-REF` for current docs referencing archived audit evidence, doc status-header debt, distribution artifact absence, process guard/runtime invariants, schema-version refs, tool-version hashes, and silent-default detections outside this docs taxonomy task.
- `cmake --preset verify`: PASS. CMake reported SDL deprecation/pkg-config warnings only; build boundary checks passed during configure.
- `cmake --build --preset verify --target ALL_BUILD`: PASS. Known duplicate-symbol linker warnings remained in the existing graphics/platform stubs.
- `ctest --preset verify -R "dominium_docs_taxonomy|smoke|Smoke" --output-on-failure`: PASS, 16/16 tests passed.

## Remaining Follow-Up

- Refresh generated AIDE/repo-map snapshots in an AIDE-owned task if those
  projections need current docs-path mirrors.
- Regenerate any historical reports only through their owning generators if
  later tasks choose to refresh them.
- Address RepoX historical-reference policy separately if current docs are no
  longer allowed to cite archived audit evidence after this taxonomy fold.
