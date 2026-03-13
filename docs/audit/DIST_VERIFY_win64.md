Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-3 clean-room distribution verification baseline

# DIST Verify - win64

- result: `complete`
- bundle_root: `dist/v0.0.0-mock/win64/dominium`
- deterministic_fingerprint: `4c112fbe56059cd83835767848a3546329f125baa84ec01b8de4be460445e6d3`

## Layout Check

- result: `complete`
- missing_paths: `none`

## Release Manifest Verification

- result: `complete`
- verified_artifact_count: `25`
- manifest_hash: `e1eb0b012222f432f88c30a4fd1e56054c4f565779f5e68ff088568cefa74eb9`

## Pack Verification

- result: `complete`
- returncode: `0`

## Descriptor Checks

- `bin/client` passed=`True` expected=`10389f5d3aaa8422af4cf7a342b1c9d97ff07c82596634ea2343ac53235d05c2` actual=`10389f5d3aaa8422af4cf7a342b1c9d97ff07c82596634ea2343ac53235d05c2`
- `bin/engine` passed=`True` expected=`8c145a8278ab2a38aca8d24e2a0b8efeb868cb1002787d3e7328df3708e630a9` actual=`8c145a8278ab2a38aca8d24e2a0b8efeb868cb1002787d3e7328df3708e630a9`
- `bin/game` passed=`True` expected=`08a671f790395f15466ea538bb3b4d14399de0c6263676780860034559374bc7` actual=`08a671f790395f15466ea538bb3b4d14399de0c6263676780860034559374bc7`
- `bin/launcher` passed=`True` expected=`633a8a256e68cefd3874091eca36697cd9d129bfdf9e219c93e15314ae836f64` actual=`633a8a256e68cefd3874091eca36697cd9d129bfdf9e219c93e15314ae836f64`
- `bin/server` passed=`True` expected=`f4a881b90ec8082962b5561da2ecd73c2050ef32b43aae925bec1160bef6048b` actual=`f4a881b90ec8082962b5561da2ecd73c2050ef32b43aae925bec1160bef6048b`
- `bin/setup` passed=`True` expected=`be061344ec1910a4203f07060e5e2e8b058b7a18f3ae952a377961862b126f11` actual=`be061344ec1910a4203f07060e5e2e8b058b7a18f3ae952a377961862b126f11`

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
