# Steam Packaging (SteamPipe depots)

## Outputs

The Steam packaging target stages:

- `dist/steam/depots/<depotid>/` (depot content; canonical artifact layout at depot root)
- `dist/steam/app_build.vdf`
- `dist/steam/depot_build_<depotid>.vdf`

## Build

```
SOURCE_DATE_EPOCH=946684800 REPRODUCIBLE=1 make package-steam BUILD_DIR=build/<your-build> VERSION=x.y.z
```

To set real Steam identifiers, invoke the pipeline directly:

```
python scripts/packaging/pipeline.py steam --artifact dist/artifacts/dominium-x.y.z --out dist/steam --version x.y.z --appid <appid> --depotid <depotid> --reproducible
```

## Depot layout (locked)

Depot root contains the canonical `artifact_root/` layout directly:

```
depots/<depotid>/
  setup/
  payloads/
  docs/
```

## Steam lifecycle → CLI mapping (design)

SteamPipe itself does not execute installers automatically; integration is achieved by using launch configuration / first-run gating.

Mapping table:

- Install / update:
  - `dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest --op install --scope portable --out <invocation>`
  - `dominium-setup plan --manifest setup/manifests/product.dsumanifest --invocation <invocation> --out <plan>`
  - `dominium-setup apply --plan <plan>`
- Verify:
  - `dominium-setup verify --state <install_root>/.dsu/installed_state.dsustate`
- Uninstall:
  - `dominium-setup export-invocation --manifest setup/manifests/product.dsumanifest --state <install_root>/.dsu/installed_state.dsustate --op uninstall --scope portable --out <invocation>`
  - `dominium-setup plan --manifest setup/manifests/product.dsumanifest --state <install_root>/.dsu/installed_state.dsustate --invocation <invocation> --out <plan>`
  - `dominium-setup apply --plan <plan>`

## Sources

- Pipeline entry: `scripts/packaging/pipeline.py` (`steam` subcommand)

