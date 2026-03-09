Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MVP Install Layout

Dominium v0.0.0 defines one portable install skeleton for the MVP runtime bundle.

## Canonical Layout

```text
dist/
  bin/
    dominium_client
    dominium_server
  packs/
    base/
      pack.base.procedural/
    official/
      pack.sol.pin_minimal/
      pack.earth.procedural/
  profiles/
    bundle.mvp_default.json
  locks/
    pack_lock.mvp_default.json
  saves/
  logs/
```

## Layout Semantics

- `bin/`
  - `dominium_client` is the bootstrap entry for CLI map view or GUI freecam view.
  - `dominium_server` is the bootstrap entry for the headless server stub.
- `packs/`
  - only the three MVP install-visible packs are present.
  - alias manifests record the canonical source pack provenance for each install-visible pack.
- `profiles/`
  - ships the canonical profile bundle artifact.
- `locks/`
  - ships the canonical pack lock artifact that must be supplied to every session bootstrap.
- `saves/`
  - local session persistence root.
- `logs/`
  - local runtime/bootstrap log root.

## Packaging Constraints

- The install layout is offline and portable.
- The install layout does not require a launcher UI.
- The install layout does not require pack downloads or service discovery.
- Pack identity is versioned and deterministic before launch.
