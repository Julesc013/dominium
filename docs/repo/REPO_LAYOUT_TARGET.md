Status: PROVISIONAL
Phase: CONVERGE-01
Supersedes: none
Superseded By: none
Stability: provisional
Replacement Target: hardened source repository layout contract after controlled CONVERGE migration

# Repository Layout Target

`contracts/repo/layout.contract.toml` is the machine-readable authority for Dominium source repository layout during convergence. This document explains that contract for human readers; the validator reads the contract, not this prose.

CONVERGE-01 does not move directories, rename roots, change build behavior, or change product, install, pack, executable, or virtual-root identity.

## Target Roots

The source repository should converge toward ownership-based top-level roots:

- `apps/`: thin product entrypoints and product composition for client, server, setup, launcher, and tools.
- `engine/`: deterministic Domino substrate and public engine contracts.
- `game/`: Dominium rules, domain process semantics, authority rules, world logic, economy, and civilization logic.
- `runtime/`: AppShell, platform, render, audio, input, network, storage, diagnostics, and UI adapters.
- `contracts/`: schemas, registries, protocols, capabilities, compatibility, stability, replay, ABI, repo, and distribution contracts.
- `content/`: packs, profiles, fixtures, datasets, assets, and authored domain data.
- `docs/`: human-readable canon, architecture, planning, audits, guides, and domain documentation.
- `tests/`: test suites, determinism checks, fixtures, and verification inputs.
- `tools/`: developer, validation, migration, CI, code generation, review, and audit tools.
- `scripts/`: repository automation and developer workflow entrypoints.
- `cmake/`: CMake modules, toolchain helpers, and build configuration helpers.
- `external/`: pinned third-party source or vendored external dependencies.
- `release/`: release definitions, package recipes, matrices, signing metadata, and publication policy inputs.
- `archive/`: historical, superseded, quarantined, generated-evidence, and legacy material retained with provenance.

Optional future roots are:

- `sdk/`: public SDK headers, samples, and SDK documentation.
- `examples/`: sample projects and examples.

## Projection Boundary

Source repository layout is not the portable install layout, runtime store layout, media layout, or distribution output layout. Those layouts are projections governed by AppShell, install, content-storage, bundle, save, instance, and future distribution contracts.

Do not infer `dist/`, `store/`, `instances/`, `saves/`, media, package, or install paths from source repo top-level roots.

## Later Phases

Later CONVERGE tasks may use the contract, inventory, and move map to plan controlled changes:

- CONVERGE-02: stale layout authority supersession.
- CONVERGE-03: root allowlist and root-file policy hardening.
- CONVERGE-05: archive, attic, legacy, and quarantine convergence.
- CONVERGE-06: contract, schema, compatibility, and lock convergence.
- CONVERGE-07: runtime, AppShell, platform, render, UI, network, and diagnostics convergence.
- CONVERGE-08: product entrypoint convergence into `apps/`.
- CONVERGE-09: mixed domain-root split.
- CONVERGE-10: blocking enforcement only after controlled moves.
