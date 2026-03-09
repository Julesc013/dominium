Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MVP Runtime Bundle

This document defines the single canonical runtime bundle for Dominium v0.0.0.
It is subordinate to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`,
and the v0.0.0 scope constitution frozen by MVP-0.

## Bundle ID

- `profile.bundle.mvp_default`

## Profile Selection

- GEO topology: `geo.topology.r3_infinite`
- GEO metric: `geo.metric.euclidean`
- GEO partition: `geo.partition.grid_zd`
- GEO projections:
  - `geo.projection.perspective_3d`
  - `geo.projection.ortho_2d`
- Realism: `realism.realistic_default_milkyway_stub`
- Physics: `physics.default_realistic`
- Law:
  - dev default: `law.lab_freecam`
  - release stub: `law.softcore_observer`
- Epistemic:
  - dev default: `epistemic.admin_full`
  - release stub: `epistemic.diegetic_default`
- Compute: `compute.default`
- Coupling: `coupling.default`
- Overlay: `overlay.default`
- Logic: `logic.default`

## Minimal Pack Set

The MVP runtime bundle requires exactly three install-visible packs:

1. `pack.base.procedural`
2. `pack.sol.pin_minimal`
3. `pack.earth.procedural`

These are distribution aliases over the current repository source packs.
They keep the install surface minimal while preserving deterministic source provenance.

## Pack Lock

- The runtime pack lock is `pack_lock.mvp_default`.
- `pack_lock_hash` is derived from:
  - the ordered alias pack hashes
  - the `profile.bundle.mvp_default` hash
- Every run must record the resulting `pack_lock_hash` in `SessionSpec`.

## Seed Policy

- Dev default:
  - explicit `--seed`, or deterministic fallback `seed=0`
- Release stub:
  - explicit user-provided seed required
- Named authoritative RNG roots are derived from:
  - `universe_seed`
  - `generator_version_id`

## Authority Defaults

- Dev default:
  - law `law.lab_freecam`
  - epistemic `epistemic.admin_full`
  - freecam bootstrap enabled
- Release stub:
  - law `law.softcore_observer`
  - epistemic `epistemic.diegetic_default`
  - explicit seed required

## Non-Goals

- No launcher shell beyond seed input and bootstrap handoff
- No online dependency
- No runtime pack discovery outside the locked bundle
- No optional pack requirement beyond the three-pack MVP set
