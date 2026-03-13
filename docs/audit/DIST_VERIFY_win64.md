Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-3 clean-room distribution verification baseline

# DIST Verify - win64

- result: `complete`
- bundle_root: `dist/v0.0.0-mock/win64/dominium`
- deterministic_fingerprint: `c4976ffdda1526f9450334d912fdbe578291c64776d34ec58bf6bffff433d5d9`

## Layout Check

- result: `complete`
- missing_paths: `none`

## Release Manifest Verification

- result: `complete`
- verified_artifact_count: `25`
- manifest_hash: `1630c519b6c04299f8eeefb4ea58a9e0af883550dfcb0d226f77fe6b3dfb7fdc`

## Pack Verification

- result: `complete`
- returncode: `0`

## Descriptor Checks

- `bin/client` passed=`True` expected=`2eee26034cc48c301f347032fe5a4529950d028a918cb166be2fa7b43144b896` actual=`2eee26034cc48c301f347032fe5a4529950d028a918cb166be2fa7b43144b896`
- `bin/engine` passed=`True` expected=`2af95fa86ba17f361ad15963191be0830584a0486c23a647d89eaf9fc0c6aadf` actual=`2af95fa86ba17f361ad15963191be0830584a0486c23a647d89eaf9fc0c6aadf`
- `bin/game` passed=`True` expected=`7f4efac2adb33087947271e1963720bfba02d9a9317559286a3dede36821997b` actual=`7f4efac2adb33087947271e1963720bfba02d9a9317559286a3dede36821997b`
- `bin/launcher` passed=`True` expected=`2e60cfb652c888b8c97eee54200e8b95ac429b3f1c10c117825515b987f98fb6` actual=`2e60cfb652c888b8c97eee54200e8b95ac429b3f1c10c117825515b987f98fb6`
- `bin/server` passed=`True` expected=`a2fd53ae23d236ffdb01f0ca1d804feddef4c09bf106211fe48d2a9ef2b206f1` actual=`a2fd53ae23d236ffdb01f0ca1d804feddef4c09bf106211fe48d2a9ef2b206f1`
- `bin/setup` passed=`True` expected=`5b665b4788c5c7c76c88068b5ab574ab5cd7709e4254860305406694156610b1` actual=`5b665b4788c5c7c76c88068b5ab574ab5cd7709e4254860305406694156610b1`

## Forbidden File Scan

- result: `complete`
- none

## Absolute Path Scan

- result: `complete`
- none

## Mode Selection Sanity

- `engine` requested=`cli` selected=`cli` passed=`True`
- `engine` requested=`tui` selected=`tui` passed=`True`
- `game` requested=`cli` selected=`cli` passed=`True`
- `game` requested=`tui` selected=`tui` passed=`True`
- `launcher` requested=`cli` selected=`cli` passed=`True`
- `launcher` requested=`tui` selected=`tui` passed=`True`
- `setup` requested=`cli` selected=`cli` passed=`True`
- `setup` requested=`tui` selected=`tui` passed=`True`

## Errors

- none

## Warnings

- `warn.release_manifest.signature_missing` `signatures`: no detached or inline signatures were provided
