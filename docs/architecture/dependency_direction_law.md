Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Owner: contracts.repo

# Dependency Direction Law

Dominium roots are ownership boundaries, not junk drawers. Dependency direction
law defines which roots may rely on which other roots and keeps public contracts
from becoming accidental implementation shortcuts.

The machine-readable law is:

```text
contracts/repo/dependency_directions.contract.toml
```

The validator is:

```powershell
python tools/validators/repo/check_dependency_directions.py --repo-root . --strict
```

## Root Meanings

`engine/` is deterministic reusable substrate. It may use contracts and approved
external portability surfaces. It must not depend on `runtime/`, `game/`,
`apps/`, `content/`, `tools/`, `release/`, or `archive/`.

`runtime/` owns host services, providers, platform bridges, render service
composition, and adapter boundaries. It may use `engine/` and `contracts/`, but
must not depend on product shells under `apps/`, tools, or archive history.

`game/` owns Dominium domain law and product-specific meaning. It may use
`engine/` and `contracts/`, and may reference content through declared
data/artifact interfaces. It must not own host/platform/UI truth or depend on
apps/tools/archive.

`apps/` are thin product shells. They may compose runtime, game, and contracts.
They may reach content only through package/profile/artifact interfaces.

`contracts/` are law. They may name paths, IDs, schemas, and registries as
metadata, but they must not import or include implementation roots.

`content/` is data. It may reference schemas/contracts by ID or path, but must
not import implementation code.

`tools/` and `tests/` may inspect all roots. That inspection does not make tools
or tests runtime dependencies. Product, runtime, engine, and game code must not
depend on tools.

`docs/` may link to anything. `release/` may reference packaged inputs as release
metadata. `archive/` is inactive retained history; active source must not depend
on it.

## Edge Types

The validator classifies dependency-like signals into:

- `include`: C/C++ preprocessor include.
- `import`: Python import.
- `build_reference`: CMake or build metadata reference.
- `path_reference`: plain path mention.
- `schema_reference` and `contract_reference`: law or schema references.
- `doc_reference`, `test_reference`, `tool_inspection`, `release_input`,
  `archive_reference`, and `unknown`.

Strict mode fails high-confidence active `include` and `import` violations. It
does not fail documentation links, test fixtures, tool inspection, archive
history, or ambiguous path references.

## When A Dependency Is Needed

Do not bypass the law. Use the narrowest correction that preserves ownership:

1. Add or use a contract if the dependency is actually a public law/data surface.
2. Move code to the owner that already has the dependency.
3. Add a runtime service or provider boundary if host/platform behavior is needed.
4. Add a precise temporary exception only with owner, reason, path, edge type, and
   retirement task.
5. Record a blocker if none of the above is safe.

Broad blanket exceptions are forbidden. Exceptions live in:

```text
contracts/repo/dependency_direction_exceptions.toml
```

## Integration

Public surfaces define identity and stability. Dependency direction decides which
owners may rely on those surfaces. The ABI canon keeps public headers from
leaking implementation or platform details across those boundaries.

This law extends, rather than replaces, existing checks:

- `scripts/verify_includes_sanity.py`
- `scripts/verify_build_target_boundaries.py`
- `scripts/verify_ui_shell_purity.py`
- `scripts/verify_abi_boundaries.py`
- `tools/validators/repo/check_public_surface.py`
- `tools/validators/abi/check_public_headers.py`

Full CTest remains T4 full/release proof. The normal proof gate is still
`fast_strict`.
