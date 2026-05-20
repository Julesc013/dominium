Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Task: PUBLIC-SURFACE-REGISTRY-01

# Public Surface Registry

Dominium's public surface registry is the machine-readable answer to which
repo surfaces are public, internal, provisional, stable, generated, fixture,
historical, or retired.

The registry lives at:

- `contracts/public_surface/public_surface.contract.toml`
- `contracts/public_surface/surface.schema.json`
- `contracts/public_surface/surface_kind.registry.json`
- `contracts/public_surface/surface_stability.registry.json`

The validator is:

```text
python tools/validators/repo/check_public_surface.py --repo-root . --strict
```

## Core Rule

Paths are not identity. Implementation is not contract. UI is not authority.
Generated output is not source truth.

Public identity must be registered through contracts, manifests, registries,
stable IDs, public headers, compatibility corpora, or release metadata. A file
or directory can expose code without becoming a stable public promise.

## Surface Classes

- Public stable surfaces are relied-on contracts. They require proof,
  compatibility policy, and a replacement path.
- Provisional surfaces are visible and named, but not promised stable.
- Internal surfaces are implementation details. They may move or change without
  downstream compatibility promises.
- Generated surfaces are emitted from source truth elsewhere and must declare
  source and generator before active use.
- Fixture surfaces are test-only.
- Historical surfaces are archival evidence only.
- Retired surfaces are known old surfaces with retirement reason and
  replacement or refusal path.

Most initial entries are intentionally provisional or internal. Stability is a
claim, not a reward for existing.

## Registering A New Surface

Add a `[[surface]]` entry with:

- `id`
- `kind`
- `path`
- `owner`
- `stability`
- `proof`
- `compatibility`
- `replacement_policy`
- `notes`

Use a dotted semantic ID:

- `domino.` for reusable substrate surfaces.
- `dominium.` for game, product, repo, release, or Dominium-specific surfaces.

The path should identify the current implementation or defining artifact, but
the ID is the surface identity.

## Promotion

Promotion from `internal` or `provisional` to a stable class requires:

- registry update
- validator pass
- non-empty proof entries
- compatibility or migration policy
- replacement or deprecation policy
- task-specific validation beyond normal fast strict when the surface is
  release, ABI, protocol, provider, save, replay, package, or command facing

Stable public API/ABI work belongs to `API-ABI-CANON-01`. Stable schema and
protocol work belongs to `SCHEMA-PROTOCOL-LAW-01`. Command surfaces belong to
`COMMAND-SURFACE-01`.

## Retirement

Retired surfaces must keep:

- `stability = "retired"`
- `retirement_reason`
- `replacement_policy`
- proof that active repo validators reject or no longer depend on the old path

Retired paths must not be recreated as active public surfaces without a new
reviewed registry change.

## Generated, Archive, And Fixture Boundaries

Generated output can be evidence or operational output, but it is not source
truth unless a stronger contract explicitly promotes the generated artifact.
Archive paths are historical by default. Fixtures are test-only and do not
create product compatibility promises.

## Relationship To AIDE, RepoX, And TestX

AIDE and Codex must use this registry before claiming a new exposed interface is
public or stable. RepoX and future TestX lanes may consume the registry to catch
unregistered public-looking surfaces. The current normal development proof gate
is still `fast_strict`; full CTest remains T4 full/release proof.

## Workbench And Command Surfaces

Workbench modules and command surfaces are registered conservatively as internal
or provisional until their later Foundation Lock tasks define stable descriptors,
command contracts, refusal behavior, and compatibility tests.
