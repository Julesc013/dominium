Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Task: PUBLIC-SURFACE-REGISTRY-01

# Public Surface Guidelines

Before exposing a new header, schema, registry, command, provider interface,
package format, save/replay format, module descriptor, or release artifact,
check the public surface registry.

```text
python tools/validators/repo/check_public_surface.py --repo-root . --strict
```

## Default Choice

Choose `internal` unless the surface is intentionally visible. Choose
`provisional` when the surface is named and visible but not yet stable.

Do not choose a stable class just because code exists, tests pass, or another
component imports it. Stability requires explicit compatibility proof.

## Stability Choices

- `internal`: implementation detail, no downstream promise.
- `provisional`: visible, named, and not yet stable.
- `experimental`: may disappear.
- `generated`: emitted from source truth; requires source and generator.
- `fixture`: tests only.
- `historical`: archive or documentation history only.
- `retired`: old surface with retirement reason and replacement policy.
- `stable_*` or `frozen_abi`: only with proof, compatibility policy, and
  replacement/deprecation policy.

## Naming

- Use `domino.` for reusable substrate surfaces.
- Use `dominium.` for game, product, repo, release, content, or project-specific
  surfaces.
- Use dotted semantic IDs ending in `.vN`.
- Keep paths repo-relative and short.
- Do not use a path as the identity.

Good:

```toml
[[surface]]
id = "domino.engine.public_headers.v1"
kind = "c_header"
path = "engine/include"
owner = "engine"
stability = "provisional"
proof = ["python scripts/verify_includes_sanity.py --repo-root ."]
compatibility = "not_yet_stable"
replacement_policy = "requires_registry_update"
notes = "Umbrella header surface; stable ABI proof comes later."
```

Bad:

```toml
[[surface]]
id = "headers"
kind = "c_header"
path = "engine/include"
owner = ""
stability = "stable_api"
proof = []
compatibility = "not_yet_stable"
replacement_policy = "none"
notes = "Exists, so it is public."
```

## Adding A Surface

1. Add or update a `[[surface]]` entry in
   `contracts/public_surface/public_surface.contract.toml`.
2. Choose a kind from `surface_kind.registry.json`.
3. Choose a stability class from `surface_stability.registry.json`.
4. Add proof commands that actually validate the surface.
5. Add a compatibility and replacement policy appropriate to the stability.
6. Run the public surface validator.
7. Run `fast_strict` before closing a normal task.

## Promotion And Retirement

Promotion to stable is a separate governance act. It must include proof and
compatibility evidence. Retirement must record a reason and replacement or
refusal path.

Future tasks will harden API/ABI, commands, diagnostics, artifacts, schemas,
provider model, and replacement protocol. Until then, most new surfaces should
stay internal or provisional.
