# macOS Packaging (PKG + DMG)

## Outputs

- `dist/macos/DominiumSetup-x.y.z.pkg`
- `dist/macos/DominiumSetup-x.y.z.dmg`

## Tooling

Required (installed separately; not downloaded by the pipeline):

- `pkgbuild`
- `productbuild`
- `hdiutil`

## Build

Enable packaging at configure time:

```
cmake -S . -B build -DDOMINIUM_ENABLE_PACKAGING=ON
```

Run on macOS:

```
cmake --build build --target package-macos
```

Artifacts land in `dist/macos/`.

## PKG behavior

- The PKG installs the canonical `artifact_root/` layout into:
  - `/Library/Application Support/Dominium/setup/artifact_root`
- The installer also ships an invocation payload:
  - `/Library/Application Support/Dominium/setup/invocation.tlv`
- The `postinstall` script is minimal and deterministic:
  - `plan --manifest <manifest> --invocation <payload> --out <plan>`
  - `apply --plan <plan>`

No other postinstall logic is permitted.

## DMG layout

The DMG contains:

- `DominiumSetup-x.y.z.pkg`
- `docs/` from the artifact root
- `SHA256SUMS`
- `artifact_manifest.json`
- optional portable archive (if provided)

## Codesign + notarization hooks (design-level)

The pipeline does not perform signing automatically. Recommended hooks:

- Sign binaries inside the staged artifact root prior to `pkgbuild`
- Sign the resulting `.pkg` with `productbuild --sign "<Developer ID Installer: ...>"`
- Notarize the signed pkg, then staple:
  - `xcrun notarytool submit ...`
  - `xcrun stapler staple DominiumSetup-x.y.z.pkg`

## Sources

- PKG build: `source/dominium/setup/installers/macos/packaging/pkg/scripts/build_pkg.sh`
- Postinstall hook: `source/dominium/setup/installers/macos/packaging/pkg/scripts/postinstall`
- DMG build: `source/dominium/setup/installers/macos/packaging/dmg/build_dmg.sh`

