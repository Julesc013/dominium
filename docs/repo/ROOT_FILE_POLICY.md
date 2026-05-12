Status: PROVISIONAL
Phase: CONVERGE-01
Supersedes: none
Superseded By: none
Stability: provisional

# Root File Policy

The repository root is a coordination surface, not a general source directory. Root-level sprawl hides ownership, weakens mechanical validation, and causes future agents to bind work to convenient paths instead of canonical owners.

## Allowed Metadata Directories

Allowed metadata/config roots are declared in `contracts/repo/layout.contract.toml` and include:

- `.github/`
- `.vscode/`
- `.aide/`
- `.aide.local.example/`

Other dot roots require explicit contract classification.

## Allowed Root Files

Allowed root files are declared in the contract and include governance, project, build, license, security, contribution, README, and version identity files:

- `AGENTS.md`
- `CLAUDE.md`
- `CMakeLists.txt`
- `CMakePresets.json`
- `CONTRIBUTING.md`
- `DOMINIUM.md`
- `GOVERNANCE.md`
- `LICENSE.md`
- `README.md`
- `SECURITY.md`
- `VERSION_*`

The contract may also allow specific existing project files such as changelogs or tool metadata. New root files should be avoided unless they are project-level coordination files and are added to the contract deliberately.

## Generated Roots

Generated roots are evidence or output, not source ownership. `build/`, `out/`, `dist/`, and `artifacts/` must not become canonical source roots merely because tooling emits them.

## `dist/`

`dist/` is a distribution/build projection unless a stronger release contract explicitly says otherwise. It is not the source repo layout and must not define source ownership.

## `build/` And `out/`

`build/` and `out/` are generated build outputs. They should not be relied on for canonical source, schema, contract, or product ownership.

## `repo/`

The existing root-level `repo/` must be classified and migrated later by ownership. Do not add new authority there. Future material should prefer `contracts/repo/`, `docs/repo/`, or `tools/migration/` depending on whether it is machine-readable contract, human documentation, or migration tooling.

## Version And Project Policy Files

`VERSION_*` files are allowed root identity files. README, license, security, contributing, governance, and agent instruction files may remain at root when they represent repository-wide coordination.
