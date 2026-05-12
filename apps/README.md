# Apps Root

Status: PROVISIONAL
Phase: CONVERGE-08

`apps/` is the source repository root for product entrypoints and thin product composition. It owns the source trees that bind Dominium products to AppShell/runtime, engine, game, contracts, and content surfaces without becoming those lower layers.

## Product Entrypoints

- `apps/client/` is the client executable and product composition surface.
- `apps/server/` is the server executable and product composition surface.
- `apps/setup/` is the setup executable and product composition surface.
- `apps/launcher/` is the launcher executable and product composition surface.
- `apps/tools/` is reserved for shipped product-tool entrypoints only after explicit classification.

Developer tooling, validators, migration tools, codegen, review tools, and CI helpers remain under `tools/`.

## Ownership Rules

Product entrypoints must stay thin. They may bind product descriptors, executable entrypoints, product-local command surfaces, and composition wiring. They must not own engine truth, game/domain law, runtime/platform/render/UI adapters, schemas/contracts, content/packs, generated package bytes, install stores, runtime logs, or media layouts.

Runtime and AppShell implementation belongs under `runtime/`. Deterministic engine substrate belongs under `engine/`. Dominium rules and domain process semantics belong under `game/`. Machine-readable contracts belong under `contracts/`. Authored content belongs under `content/` or the current transitional content roots until later convergence.

Root-level `client/`, `server/`, `setup/`, and `launcher/` are retired after CONVERGE-08. Do not recreate them as source-authority roots. Executable names, product IDs, install IDs, pack IDs, virtual-root IDs, and command behavior remain stable.
