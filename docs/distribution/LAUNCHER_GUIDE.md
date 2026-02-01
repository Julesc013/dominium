Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Launcher Guide (LAUNCH-GUIDE)

Status: evolving.
Scope: launcher usage (CLI canonical, TUI/GUI wrappers).

## Quick start (60-second rule)
The launcher works with three primitives:
- **Install**: read-only binaries.
- **Instance**: mutable data root.
- **Profile**: advisory defaults (casual/hardcore/creator/server).

Select an install, create/select an instance, pick a profile, then run:
```
launcher installs list --search <root>
launcher installs select --manifest <install_root>/install.manifest.json --state-root <state_root>
launcher instances create --install-manifest <install_root>/install.manifest.json --data-root <instance_root> --profile org.dominium.profile.casual
launcher preflight --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json
launcher run --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json --run-mode play --confirm
```

## Installs
List installs and select one explicitly:
```
launcher installs list --search <root>
launcher installs select --manifest <install_root>/install.manifest.json --state-root <state_root>
launcher installs active --state-root <state_root>
```

## Instances
Create, clone, fork, activate, and delete instances:
```
launcher instances create --install-manifest <install_root>/install.manifest.json --data-root <instance_root> --profile org.dominium.profile.casual
launcher instances clone --source-manifest <instance_root>/instance.manifest.json --data-root <new_root>
launcher instances fork --source-manifest <instance_root>/instance.manifest.json --data-root <new_root>
launcher instances activate --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json
launcher instances delete --instance-manifest <instance_root>/instance.manifest.json --confirm
launcher instances delete --instance-manifest <instance_root>/instance.manifest.json --confirm --delete-data
```

## Profiles
Profiles are advisory and do not change simulation semantics.
```
launcher profiles list
launcher instances set-profiles --instance-manifest <instance_root>/instance.manifest.json --profile org.dominium.profile.creator --confirm
```

## Preflight and run modes
Preflight always generates a compat_report. Run modes are explicit:
- play (client + local server)
- client (remote server)
- server (headless)
- inspect (read-only)
- replay (read-only replay)

```
launcher preflight --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json --run-mode play
launcher run --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json --run-mode play --confirm
```

Degraded/frozen/inspect-only runs require `--confirm`.

## Packs and sources
Packs are visible, never assumed. The launcher shows required/optional packs:
```
launcher packs list --install-manifest <install_root>/install.manifest.json --instance-manifest <instance_root>/instance.manifest.json
launcher packs add --pack-path <pack_dir> --data-root <instance_root> --confirm
launcher packs remove --pack-id <pack_id> --data-root <instance_root> --confirm
```

## Bundles
Bundles are explicit and preflighted:
```
launcher bundles inspect --bundle <bundle_root>
launcher bundles import --bundle <bundle_root> --confirm
launcher bundles export --bundle-type replay --artifact <replay_file> --lockfile <capability.lock> --out <bundle_out>
launcher bundles import-save --bundle <bundle_root> --confirm
launcher bundles import-replay --bundle <bundle_root> --confirm
launcher bundles import-modpack --bundle <bundle_root> --confirm
launcher bundles export-instance --instance-manifest <instance_root>/instance.manifest.json --out <bundle_out>
```

## Diagnostics access
Paths are discoverable without advanced mode:
```
launcher paths --instance-manifest <instance_root>/instance.manifest.json
```

## Offline-first behavior
All launcher operations work without network access. Missing remote packs
produce explicit messages and compat_report modes.

## See also
- `docs/distribution/LAUNCHER_SCOPE.md`
- `docs/distribution/LAUNCHER_SETUP_CONTRACT.md`
- `docs/ui/LAUNCHER_WALKTHROUGH.md`