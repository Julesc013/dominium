Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: install profiles, update-model release indices, and trust-policy resolution surfaces

# Component Graph Baseline

## Component List

- `binary.client` kind=`binary` version=`0.0.0`
- `binary.engine` kind=`binary` version=`0.0.0`
- `binary.game` kind=`binary` version=`0.0.0`
- `binary.launcher` kind=`binary` version=`0.0.0`
- `binary.server` kind=`binary` version=`0.0.0`
- `binary.setup` kind=`binary` version=`0.0.0`
- `docs.release_notes` kind=`docs` version=`v0.0.0-mock`
- `lock.pack_lock.mvp_default` kind=`lock` version=`0.0.0`
- `manifest.appshell.runtime` kind=`manifest` version=`0.0.0`
- `manifest.compat.negotiation` kind=`manifest` version=`0.0.0`
- `manifest.instance.default` kind=`manifest` version=`1.0.0`
- `manifest.lib.runtime` kind=`manifest` version=`0.0.0`
- `manifest.pack_compat.runtime` kind=`manifest` version=`0.0.0`
- `manifest.release_manifest` kind=`manifest` version=`1.0.0`
- `pack.base.procedural` kind=`pack` version=`0.0.0`
- `pack.earth.procedural` kind=`pack` version=`0.0.0`
- `pack.sol.pin_minimal` kind=`pack` version=`0.0.0`
- `profile.bundle.mvp_default` kind=`profile` version=`0.0.0`

## Edge List

- `binary.client` requires `binary.engine`
- `binary.client` requires `lock.pack_lock.mvp_default`
- `binary.client` requires `manifest.appshell.runtime`
- `binary.client` requires `manifest.compat.negotiation`
- `binary.client` requires `profile.bundle.mvp_default`
- `binary.engine` requires `manifest.appshell.runtime`
- `binary.game` requires `binary.engine`
- `binary.game` requires `lock.pack_lock.mvp_default`
- `binary.game` requires `profile.bundle.mvp_default`
- `binary.launcher` recommends `docs.release_notes`
- `binary.launcher` recommends `manifest.instance.default`
- `binary.launcher` requires `binary.setup`
- `binary.launcher` requires `manifest.appshell.runtime`
- `binary.launcher` requires `manifest.compat.negotiation`
- `binary.launcher` requires `manifest.lib.runtime`
- `binary.server` requires `binary.engine`
- `binary.server` requires `lock.pack_lock.mvp_default`
- `binary.server` requires `manifest.appshell.runtime`
- `binary.server` requires `manifest.compat.negotiation`
- `binary.server` requires `profile.bundle.mvp_default`
- `binary.setup` requires `manifest.appshell.runtime`
- `binary.setup` requires `manifest.lib.runtime`
- `binary.setup` requires `manifest.pack_compat.runtime`
- `binary.setup` requires `manifest.release_manifest`
- `lock.pack_lock.mvp_default` requires `pack.base.procedural`
- `lock.pack_lock.mvp_default` requires `pack.earth.procedural`
- `lock.pack_lock.mvp_default` requires `pack.sol.pin_minimal`
- `manifest.instance.default` requires `lock.pack_lock.mvp_default`
- `manifest.instance.default` requires `profile.bundle.mvp_default`
- `profile.bundle.mvp_default` provides `provides.profile.bundle.v1`

## Resolution Algorithm

- stable lexical traversal by `component_id`
- expand `requires`, then `recommends`, then provider bindings
- deterministic provides resolution through the LIB provider resolver
- strict conflicts refuse

## Readiness

- DIST-REFINE-1 install profiles: ready
- update-model release indices: ready

## Report Fingerprints

- graph hash: `4e425dd78992c50b0460dc42ee9ecf1aa6f29df8d3acd8f859a8f1c79f975215`
- plan fingerprint: `9e509967718ab6ccf4ca9bc3e543fa2aaa480c64e128b1e40e88a72dfb3245f8`
- report fingerprint: `62e375f2ecf8f70d901ca23f686c05566e6b91d950dc034058147821e1357a1a`
