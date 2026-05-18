Status: CANONICAL
Last Reviewed: 2026-05-18
Supersedes: interim bad-root exception layout as final target shape
Superseded By: none

# Final Repository Structure

Dominium is structured as a deterministic operating-environment repository, not
as a loose game, engine, or tools pile. Directory names express ownership.

## Top Level

```text
dominium/
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

Generated/local-only roots:

```text
.aide.local/
.dominium.local/
build/
out/
dist/
```

Optional future roots require a new contract before use:

```text
sdk/
examples/
```

## Ownership Planes

- `apps/`: thin product entrypoints and product-specific shells.
- `engine/`: deterministic C89 substrate, identity, time, math, state,
  execution, replay, proof, and diagnostics.
- `game/`: simulation meaning, law, rules, processes, worlds, scenarios, and
  domain implementations.
- `runtime/`: shell, capabilities, components, platform adapters, render/input,
  audio, network, storage, IPC, package/profile/update services, and host
  diagnostics.
- `contracts/`: machine-readable law, schemas, registries, ABI, protocols,
  manifests, policies, compatibility, release, package, and repo contracts.
- `content/`: authored assets, bundles, defaults, domains, examples, fixtures,
  locale, packs, profiles, templates, and themes.
- `docs/`: human explanation, audits, runbooks, validation notes, and design
  context. Normative policy must also exist under `contracts/`.
- `tests/`: proof, fixtures, smoke, regression, determinism, performance, and
  package/release validation.
- `tools/`: validators, migration, codegen, audit, repo/build/release tooling.
- `scripts/`: thin human or CI wrappers only.
- `cmake/`: CMake modules, presets, toolchains, and build helpers.
- `external/`: third-party or vendor material with quarantined ownership.
- `release/`: release recipes, channels, packaging, signing, update manifests,
  and internal pilot distribution definitions.
- `archive/`: historical, superseded, generated retained evidence, and
  quarantine material.

## Preferred Internal Names

Future cleanup should prefer:

```text
runtime/shell/
game/domain/
content/domains/
contracts/schema/
contracts/registry/
contracts/package/
contracts/profile/
contracts/protocol/
contracts/projection/
```

Existing transitional names are not physically renamed by `MOVE-ROUTER-00`.
Later apply/repair tasks must provide shim or reference-rewrite evidence before
renaming active paths.

## Roots To Eliminate

The following top-level roots are transitional debt only:

```text
core/
control/
data/
packs/
profiles/
bundles/
compat/
lib/
libs/
locks/
repo/
safety/
security/
specs/
updates/
meta/
governance/
performance/
validation/
modding/
models/
templates/
net/
ide/
```

`MOVE-ROUTER-00` routes all tracked files under these roots in dry-run form.
`MOVE-ROUTER-01` may apply a reviewed safe subset; unknown files should move to
`archive/quarantine/<root>/`, not remain under bad roots.
