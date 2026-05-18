Status: CANONICAL
Last Reviewed: 2026-05-18
Supersedes: MOVE-BULK B-G micro-planning as the active cleanup path
Superseded By: none

# Bad Root Routing

`MOVE-ROUTER-00` defines the dry-run routing law for former bad roots. It does
not move files. It creates the route table that a later reviewed apply task can
consume with `git mv`.

## Rule

Known files route to their semantic owner. Unknown or ambiguous files route to
`archive/quarantine/<root>/` by original root. This keeps the final root cleanup
moving without pretending unclear files belong to an active subsystem.

The router must preserve file contents, contract IDs, package IDs, profile IDs,
bundle IDs, schema versions, hashes, locks, and compatibility declarations. A
path move is storage relocation only.

## Final Roots

Active source roots are:

```text
.aide/
.github/
.vscode/
apps/
engine/
game/
runtime/
contracts/
content/
docs/
tests/
tools/
scripts/
cmake/
external/
release/
archive/
```

Generated/local roots are `.aide.local/`, `.dominium.local/`, `build/`, `out/`,
and `archive/generated/dist/`.

## Bad Roots

The router covers:

```text
core control data packs profiles bundles compat lib libs locks repo safety
security specs updates meta governance performance validation modding models
templates net ide
```

`ide/` is already retired in the current tracked state, but remains in the
contract so a regression is routed instead of silently tolerated.

## Root Routing Summary

- `templates/`: schemas to `contracts/schema/templates/`, contract/manifest
  material to `contracts/templates/`, examples to
  `content/examples/templates/`, docs to `docs/development/templates/`, payloads
  to `content/templates/`.
- `models/`: schemas to `contracts/schema/models/`, registries to
  `contracts/registry/models/`, assets to `content/assets/models/`, domain data
  to `content/domains/models/`, docs to `docs/domains/models/`.
- `modding/`: schemas to `contracts/schema/modding/`, package/capability law to
  `contracts/package/modding/` or `contracts/capability/modding/`, examples to
  `content/examples/modding/`, docs to `docs/modding/`.
- `data/`, `packs/`, `profiles/`, `bundles/`: authored payloads route to
  `content/`; schemas and registries route to `contracts/`; fixtures route to
  `tests/fixtures/`; release bundle recipes route to `release/packaging/`.
- `compat/`, `locks/`, `repo/`, `safety/`, `security/`, `specs/`, `updates/`:
  normative material routes to `contracts/`, validators/tools to `tools/`, docs
  to `docs/`, release/update recipes to `release/`.
- `validation/`, `meta/`, `governance/`, `performance/`: active tools route to
  `tools/`, fixtures and benchmarks to `tests/`, machine-readable law to
  `contracts/`, docs to `docs/`.
- `core/`, `control/`, `net/`, `lib/`, `libs/`: deterministic substrate routes
  to `engine/`, game law to `game/`, runtime/platform/network material to
  `runtime/`, ABI and protocols to `contracts/`, vendor material to `external/`,
  tools to `tools/`, docs to `docs/`.

Every root also has an explicit quarantine fallback under `archive/quarantine/`.

## Forbidden Target Names

The router must not propose target directory segments named `src`, `source`,
`sources`, `code`, `impl`, `common`, `shared`, `misc`, `new`, `old`, `future`,
`modern`, `legacy`, `classic`, `universal`, `experimental`, `research`, `v2`,
`v3`, or root `compat`.

Allowed exceptions are `archive/legacy/`, `contracts/compatibility/`, and
`docs/compatibility/`. Dry-run target paths that would otherwise preserve a
forbidden segment are sanitized to explicit payload names and must be reviewed
before apply.

## Dry Run

Use:

```powershell
python tools/migration/route_bad_roots.py --repo-root . --dry-run --include-quarantine --fail-on-collision --json-out .aide/reports/MOVE-ROUTER-00-dry-run.json --md-out .aide/reports/MOVE-ROUTER-00-dry-run.md --route-table-out .aide/reports/MOVE-ROUTER-00-route-table.json --skipped-out .aide/reports/MOVE-ROUTER-00-skipped-or-quarantined.md
```

`MOVE-ROUTER-00` apply mode is disabled. The next apply task must consume the
route table, review collisions/quarantine paths, update references, and only
then retire exceptions.

## Next Task

`MOVE-ROUTER-01 - Apply Deterministic Bad-Root Router Safe Subset`.

## MOVE-ROUTER-01 Result

MOVE-ROUTER-01 applied the route table with `git mv`.

- Bad-root tracked files before: 1,765.
- Bad-root tracked files after: 0.
- Semantic moves: 1,694.
- Quarantine moves: 71.
- Skipped moves: 0.
- Target collisions: 0.
- Active bad-root exceptions retired: 23.

Broad reference/import/build repair is assigned to
`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`.

## MOVE-ROUTER-02 Repair Status

MOVE-ROUTER-02 kept the routed structure intact and repaired a first active
reference/import/build layer.

- Bad-root tracked files after repair: 0.
- CMake configure: PASS.
- Integrated fast/smoke tests in the build pass: PASS.
- Broader TestX: FAIL.

Remaining work is assigned to `MOVE-ROUTER-02R`; no task may restore former bad
roots as active owners to avoid that repair work.
