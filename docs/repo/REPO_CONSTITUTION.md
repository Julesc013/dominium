# Repo Constitution

## Status

- Status: PROVISIONAL
- Phase: AIDE-STRUCTURE-00
- Machine-readable sources:
  - `contracts/repo/root_constitution.toml`
  - `contracts/repo/ownership_slots.toml`
  - `contracts/repo/layout.contract.toml`
  - `contracts/repo/root_allowlist.toml`
  - `contracts/repo/layout_exceptions.toml`

## Why This Exists

Dominium has had root sprawl. The post-CONVERGE repo is much more coherent,
but it still contains exception-backed roots that mix implementation, content,
contracts, generated evidence, release material, and old tool surfaces.

Future restructuring must be mechanical, not visual drag/drop. AIDE owns the
refactor control plane: inventory, classification, salvage maps, move maps,
reference rewrites, validation, evidence ledgers, and rollback notes. Dominium
architecture remains Dominium architecture.

Top-level roots should be durable long-term ownership slots. Internal paths can
evolve through reviewed AIDE move maps after evidence proves identity,
references, tests, and rollback behavior.

## Stable Top-Level Roots

- `.aide/`: committed AIDE control-plane policy, queues, ledgers, reports,
  context, and task specs.
- `.github/`: GitHub workflows and repository integration.
- `apps/`: thin product entrypoints and product composition.
- `engine/`: deterministic engine substrate.
- `game/`: Dominium rules, simulation, and game domains.
- `runtime/`: AppShell, platform, render, audio, input, network, storage, UI,
  diagnostics, and host-facing adapters.
- `contracts/`: machine-readable and normative schemas, registries, ABI,
  protocols, capabilities, replay, repo, build, and distribution contracts.
- `content/`: authored packs, profiles, templates, fixtures-as-content, assets,
  and domain data.
- `docs/`: human-readable explanation, architecture, audits, guides, and
  operations.
- `tests/`: tests, fixtures, golden cases, integration, determinism, and
  regression.
- `tools/`: validators, generators, audit, repo, test, build, migration, and
  AIDE adapters.
- `scripts/`: small workflow wrappers and entrypoints.
- `cmake/`: CMake modules and toolchain/build glue.
- `external/`: vendored or referenced third-party material.
- `release/`: release recipes, package policy, signing, channels, and release
  inputs.
- `archive/`: historical, superseded, quarantined, and generated-evidence
  snapshots.

## Generated And Local Roots

`dist/`, `build/`, and `out/` are generated output roots. `.dominium.local/`
and `.aide.local/` are ignored local machine or AIDE state roots. They are not
source authority, even when a task records evidence about them.

Tracked exception-backed generated or evidence surfaces such as `artifacts/`
remain governed by `contracts/repo/layout_exceptions.toml` until a future
evidence-policy task retires or relocates them.

## Transitional Roots

The following names are not endorsed as stable roots:

- `core`
- `control`
- `data`
- `packs`
- `profiles`
- `bundles`
- `compat`
- `lib`
- `libs`
- `locks`
- `repo`
- `safety`
- `security`
- `specs`
- `updates`
- `meta`
- `governance`
- `ide`
- `performance`
- `validation`
- `modding`
- `models`
- `templates`
- `net`

They are exception-backed review surfaces. Future tasks must classify them
file-by-file and preserve identity, references, and validation behavior before
moving anything.

## New Root Policy

Default: no new root.

A new top-level root requires:

1. distinct lifecycle
2. not cleanly owned by existing stable roots
3. durable multi-year name
4. not named after temporary phase, support status, era, or implementation
   detail
5. validator and ownership contract updated in the same change

## Paths Are Not Identity

Packs, profiles, artifacts, schemas, and release inputs are valid by manifests,
IDs, schema versions, hashes, contracts, and authority rules, not merely by
where files sit today. Paths are storage. Contracts, manifests, IDs, and hashes
define identity.

This matters because moving a path can accidentally change an identity contract
if references, embedded relative paths, hashes, distribution projections, or
compatibility shims are not updated and proven together.

## Refactor Process

The canonical flow is:

```text
inventory -> classify -> salvage map -> move map -> reference rewrite -> validators -> build/test proof -> evidence ledger -> shim retirement
```

No step implies the next step is approved. An inventory is not a move map. A
salvage map is not permission to delete. A path alias is temporary compatibility
evidence, not new identity.

## Agent Rules

- Do not manually drag/drop roots.
- Do not move mixed roots wholesale.
- Do not delete old tools because names are bad.
- Do not add new root-level folders without contract update.
- Do not treat XStack/AuditX/RepoX/TestX as product architecture.
- Use AIDE work units for inventory, classification, maps, reference rewrites,
  validation, evidence, and rollback planning.
