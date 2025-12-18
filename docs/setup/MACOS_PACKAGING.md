# macOS Packaging (PKG + DMG)

## Outputs

- `dist/macos/Dominium-x.y.z.pkg`
- `dist/macos/Dominium-x.y.z.dmg`

## Tooling

Required (installed separately; not downloaded by the pipeline):

- `pkgbuild`
- `productbuild`
- `hdiutil`

## Build

Run on macOS:

```
SOURCE_DATE_EPOCH=946684800 REPRODUCIBLE=1 make package-macos BUILD_DIR=build/<your-build> VERSION=x.y.z
```

Artifacts land in `dist/macos/`.

## PKG behavior (design)

- The PKG installs the canonical `artifact_root/` layout into:
  - `/Library/Application Support/Dominium/artifact_root`
- A minimal `postinstall` script invokes `dominium-setup` only:
  - `plan --op install --scope system`
  - `apply --plan <generated>`

No other postinstall logic is permitted.

## DMG layout (spec)

The DMG contains:

- `Dominium-x.y.z.pkg`

## Codesign + notarization hooks (design-level)

The pipeline does not perform signing automatically. Recommended hooks:

- Sign binaries inside the staged artifact root prior to `pkgbuild`
- Sign the resulting `.pkg` with `productbuild --sign "<Developer ID Installer: ...>"`
- Notarize the signed pkg, then staple:
  - `xcrun notarytool submit ...`
  - `xcrun stapler staple Dominium-x.y.z.pkg`

## Sources

- Postinstall hook: `scripts/packaging/macos/pkg_scripts/postinstall`
- Pipeline entry: `scripts/packaging/pipeline.py` (`macos` subcommand)

