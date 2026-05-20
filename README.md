# Dominium

Dominium is a deterministic civilization and industry simulation game built on
the Domino engine.

The game is about invention, production, logistics, economics, trust,
communication, settlement, and institutional power emerging from lawful
simulation rather than scripted outcomes. Players and systems act through
explicit authority, capability, and law surfaces; the simulation records
provenance and refuses invalid action deterministically.

## Home Point

Use this README as the project home point. It orients the product, repository,
and common commands. Normative engineering authority lives in the canon,
contracts, and registries linked below.

- Canon: `docs/canon/constitution_v1.md`
- Glossary: `docs/canon/glossary_v1.md`
- Canon index: `docs/architecture/CANON_INDEX.md`
- Build guide: `docs/development/guides/BUILDING.md`
- Language baseline: `docs/development/LANGUAGE_BASELINE.md`
- Public surface registry: `docs/architecture/public_surface_registry.md`
- API/ABI canon: `docs/architecture/api_abi_canon.md`
- Contributing: `CONTRIBUTING.md`
- Security: `SECURITY.md`

## Product Shape

Dominium is organized as a product suite around one simulation substrate:

- **Client**: presentation, input, perception, and command projection.
- **Server**: authoritative session execution and law validation.
- **Launcher**: profiles, instances, compatibility, and product orchestration.
- **Setup**: installation, repair, and local product configuration.
- **Tools**: validation, inspection, authoring, packaging, audit, and developer
  workflows.

The Domino engine provides deterministic mechanisms. Dominium game code defines
meaning, rules, processes, law targets, and content interpretation on top of
engine contracts.

## Design Principles

- **Determinism first**: identical canonical inputs produce identical
  authoritative outputs.
- **Process-only mutation**: authoritative state changes through lawful,
  deterministic process execution.
- **Truth, perception, render separation**: truth is authoritative; perception
  is filtered by law and authority; rendering is presentation only.
- **Explicit refusal**: invalid or unsupported action returns deterministic,
  auditable refusal rather than silent fallback.
- **Pack-driven integration**: optional content and capability surfaces are
  declared by packs, registries, schemas, and contracts.
- **Replaceable implementation**: public identity lives in stable contracts,
  manifests, registries, headers, and compatibility proof, not incidental paths.

## Repository Map

- `apps/`: product applications and shells.
- `engine/`: Domino deterministic engine substrate and public engine headers.
- `game/`: Dominium rules, process emission, and game-domain interpretation.
- `runtime/`: platform, shell, service, and runtime integration layers.
- `contracts/`: machine-readable governance, ABI, build, repo, and surface law.
- `content/`: authored content and packs.
- `docs/`: canon, architecture, development, reference, and repo documentation.
- `tests/`: contract, invariant, smoke, integration, and proof suites.
- `tools/`: validators, packaging tools, migration tools, and developer tooling.

## Language And Platform Baseline

Dominium mainline uses:

- **C17** for C code.
- **C++17** for C++ code.
- A **C-compatible public ABI** for stable binary-facing surfaces.

The active platform floor is Windows 7 SP1, macOS 10.9.5, and Linux. C++17
language mode is allowed, but the standard-library subset is restricted for
macOS 10.9.5 compatibility. Public ABI boundaries do not expose C++ classes,
STL types, exceptions, RTTI, allocator objects, or compiler object layout.

## Build And Verify

Configure and build the normal verify preset:

```powershell
cmake --preset verify
cmake --build --preset verify --target ALL_BUILD
```

Run the normal development proof gate:

```powershell
python tools/test/run_fast_strict.py --repo-root .
```

Run the language baseline validators directly:

```powershell
python tools/validators/build/check_language_baseline.py --repo-root . --strict
python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict
```

Full release and certification proof is intentionally separate from the normal
development loop. Use the test-tier contract for the distinction between normal,
extended, release, and full proof gates:

```text
contracts/testing/test_tiers.contract.toml
```

## Public Surfaces

Dominium treats public identity as an explicit contract. A path or implementation
file is not public merely because it exists.

Public, internal, generated, fixture, historical, and retired surfaces are
registered under:

```text
contracts/public_surface/public_surface.contract.toml
```

Public ABI rules are defined under:

```text
contracts/abi/c_api.contract.toml
contracts/abi/language_boundary.contract.toml
```

## Content And Modding

Content is data-driven and pack-oriented. Packs and registries describe optional
content, capabilities, compatibility, and activation surfaces. Missing optional
content must degrade or refuse explicitly; hidden fallback behavior is not part
of the product model.

See:

- `MODDING.md`
- `content/`
- `contracts/public_surface/public_surface.contract.toml`

## Documentation

Use the canon and contracts for authority, then architecture and development
docs for implementation guidance.

- Product overview: `DOMINIUM.md`
- Architecture map: `docs/architecture/CANONICAL_SYSTEM_MAP.md`
- Services and products: `docs/architecture/SERVICES_AND_PRODUCTS.md`
- Build matrix: `docs/development/BUILD_MATRIX.md`
- C17 usage policy: `docs/development/C17_USAGE_POLICY.md`
- C++17 usage policy: `docs/development/CPP17_USAGE_POLICY.md`
- macOS 10.9 C++17 subset: `docs/development/MACOS_10_9_CPP17_LIBRARY_SUBSET.md`

## Contributing

Contributions should preserve deterministic behavior, authority boundaries,
public surface registration, and the normal proof gate. Start with:

```text
CONTRIBUTING.md
```

## License And Security

- License: `LICENSE.md`
- Security policy: `SECURITY.md`
