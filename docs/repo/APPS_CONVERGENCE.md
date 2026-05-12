# Apps Convergence

Status: PROVISIONAL
Phase: CONVERGE-08

CONVERGE-08 converged Dominium product entrypoint roots into `apps/` without changing product semantics, executable names, product IDs, install IDs, pack IDs, virtual-root IDs, AppShell mode routing, or command behavior.

## What Moved

- `client/` moved to `apps/client/`.
- `server/` moved to `apps/server/`.
- `setup/` moved to `apps/setup/`.
- `launcher/` moved to `apps/launcher/`.

Required CMake, script, validator, and active tooling path references were updated to the new source paths. Developer tools remain under `tools/`.

## What Did Not Move

No domain roots were split. No engine truth moved out of `engine/`. No game/domain law moved out of `game/`. No runtime/AppShell implementation moved in this phase except path references needed to locate product entrypoints. No contracts, content, generated output, package bytes, renderer backends, platform backends, or GUI features were introduced.

## Boundaries

`apps/` is not `runtime/`: runtime owns AppShell, platform, render, UI adapter, I/O, storage, and diagnostics infrastructure.

`apps/` is not `engine/`: engine owns deterministic substrate and must not depend on product entrypoints.

`apps/` is not `game/`: game owns Dominium rules, domain process semantics, authority rules, and simulation law.

`apps/` is not `contracts/`: schemas, registries, compatibility rules, capabilities, and machine-readable layout contracts stay under `contracts/`.

`apps/` is not `content/`: packs, profiles, fixtures, datasets, and assets stay under content/data ownership surfaces until later convergence.

Product entrypoints are thin composition surfaces. They may bind product descriptors and executable entrypoints, but product semantics must flow through contracts, runtime, engine, game, and content layers. Product-specific UI shell code must remain thin and contract-bound.

Shipped product tools may use `apps/tools/` only after explicit classification. Developer tools, validators, migration tooling, codegen, review tooling, and CI helpers remain under `tools/`.

## Future Work

- CONVERGE-09: split domain roots into contracts, game, content, docs, and tests.
- CONVERGE-10: enable blocking validators after physical convergence.
- CONVERGE-11: add product, platform, render, native, toolchain, and packaging matrices.
- CONVERGE-12: stale-doc and cross-reference cleanup.
