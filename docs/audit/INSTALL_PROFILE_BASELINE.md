Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST/UPDATE-MODEL
Replacement Target: release-index governed install profiles with trust-policy and acquisition planning

# Install Profile Baseline

## Profile Definitions

- `install.profile.client` required=`binary.client, manifest.instance.default, manifest.release_manifest` optional=`binary.launcher, binary.setup, docs.release_notes`
- `install.profile.full` required=`binary.client, binary.game, binary.launcher, binary.server, binary.setup, docs.release_notes, manifest.instance.default, manifest.release_manifest` optional=`none`
- `install.profile.sdk` required=`docs.release_notes, manifest.release_manifest` optional=`binary.setup`
- `install.profile.server` required=`binary.server, manifest.instance.default, manifest.release_manifest` optional=`binary.launcher, binary.setup, docs.release_notes`
- `install.profile.tools` required=`binary.setup, manifest.release_manifest` optional=`binary.launcher, docs.release_notes`

## Resolved Component Sets

- `install.profile.client` -> `binary.client, binary.engine, lock.pack_lock.mvp_default, manifest.appshell.runtime, manifest.compat.negotiation, manifest.instance.default, manifest.release_manifest, pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal, profile.bundle.mvp_default`
- `install.profile.full` -> `binary.client, binary.engine, binary.game, binary.launcher, binary.server, binary.setup, docs.release_notes, lock.pack_lock.mvp_default, manifest.appshell.runtime, manifest.compat.negotiation, manifest.instance.default, manifest.lib.runtime, manifest.pack_compat.runtime, manifest.release_manifest, pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal, profile.bundle.mvp_default`
- `install.profile.sdk` -> `docs.release_notes, manifest.release_manifest`
- `install.profile.server` -> `binary.engine, binary.server, lock.pack_lock.mvp_default, manifest.appshell.runtime, manifest.compat.negotiation, manifest.instance.default, manifest.release_manifest, pack.base.procedural, pack.earth.procedural, pack.sol.pin_minimal, profile.bundle.mvp_default`
- `install.profile.tools` -> `binary.setup, manifest.appshell.runtime, manifest.lib.runtime, manifest.pack_compat.runtime, manifest.release_manifest`

## Readiness

- UPDATE-MODEL-0 release-index availability: ready
- Dist assembly profile selection: ready

## Report Fingerprints

- install profile registry hash: `1a741683731a38153581d96e39be794de5adcc86e3f62b5a3c36cff201740eef`
- report fingerprint: `b4654edc61464fb9ab3dd33da18a728ce3755482cfe6dbdfc73ebc18fe446691`
