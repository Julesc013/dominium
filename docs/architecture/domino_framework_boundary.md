Status: CANONICAL
Last Reviewed: 2026-05-24
Supersedes: none
Superseded By: none
Stability: provisional
Task: DOMINO-FRAMEWORK-BOUNDARY-01

# Domino Framework Boundary

## Doctrine

Domino Framework is not a top-level source root.

Domino Framework is the registered reusable surface made from:

- public surface declarations in `contracts/public_surface/`
- ABI law in `contracts/abi/`
- service law in `contracts/service/`
- provider law in `contracts/provider/`
- capability and refusal law in `contracts/capability/`
- public C-compatible headers under `engine/include/domino/`
- public C-compatible runtime headers under `runtime/include/domino/`
- provider profiles under `release/profiles/`
- conformance and boundary tests under `tests/`

The current Domino reference implementation remains in `engine/` and
`runtime/`. The current Dominium product implementation remains in `game/`,
`content/`, and `apps/`.

## Non-Roots

Do not add these as active top-level source roots:

```text
framework/
profiles/
labs/
modules/
plugins/
services/
sdk/
```

If an external SDK package is needed later, generate or assemble it from
registered public surfaces under release ownership, for example `release/sdk/`.
Do not create `sdk/` as an internal source root.

## Public Header Homes

Reusable public headers are registered surfaces, not path-derived authority:

```text
engine/include/domino/   deterministic engine API surface
runtime/include/domino/  runtime service/provider API surface
game/include/dominium/   Dominium game/product API surface
```

The public surface registry records these homes. Stability still depends on the
surface entry, ABI law, compatibility policy, proof, and replacement policy.
Visible headers are not automatically frozen ABI.

## Provider Boundary

Provider implementations are service-first:

```text
runtime/<service>/providers/<provider>/
```

Provider identity is a dotted provider ID such as:

```text
domino.provider.render.raylib.v1
```

The implementation directory is only a hint. Apps do not encode provider
choice:

```text
bad:  apps/client/rendered/raylib/
good: apps/client/ plus release/profiles/dev/client.raylib.toml
```

Cross-service helper code for a third-party suite may use:

```text
runtime/provider/suite/<suite>/
```

only when real shared helper code exists. Service implementations still belong
under `runtime/<service>/providers/<provider>/`.

## Profiles

`release/profiles/` contains development, validation, build, and release provider
recipes.

`content/profiles/` contains authored runtime, user, or game profile payloads.

Top-level `profiles/` is retired and must not be recreated.

## Enforcement

The focused validator is:

```text
python tools/validators/repo/check_domino_framework_boundary.py --repo-root . --strict
```

It verifies that framework-ness emerges from contracts, public headers, profiles,
providers, and tests rather than from a new `framework/` root.
