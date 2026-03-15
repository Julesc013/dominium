Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-3 clean-room distribution verification baseline

# DIST Verify - win64

- result: `complete`
- bundle_root: `dist/v0.0.0-mock/win64/dominium`
- deterministic_fingerprint: `1ff37f176bcee282b8c235fa18ae822107766187d3ee0bfd4a8a3eb641e55743`

## Layout Check

- result: `complete`
- missing_paths: `none`

## Release Manifest Verification

- result: `complete`
- verified_artifact_count: `25`
- manifest_hash: `52b5638abe47d665833ca9241d3a7cbe63306918769758fffa8d6094f28c1841`

## Pack Verification

- result: `complete`
- returncode: `0`

## Descriptor Checks

- `bin/client` passed=`True` expected=`34fd0035af11b634d4a5180d76b81b9fd8f8fcd6c8079ca6cff7ff30666a3e86` actual=`34fd0035af11b634d4a5180d76b81b9fd8f8fcd6c8079ca6cff7ff30666a3e86`
- `bin/engine` passed=`True` expected=`d33f608afc35402b65ba06e912db8984f992c855a475bc166570e0b35a3fee36` actual=`d33f608afc35402b65ba06e912db8984f992c855a475bc166570e0b35a3fee36`
- `bin/game` passed=`True` expected=`ef2c0f08e623cdc566bf62f4b6af1fa87b7110778390f4e9ee4bfdc647ef4736` actual=`ef2c0f08e623cdc566bf62f4b6af1fa87b7110778390f4e9ee4bfdc647ef4736`
- `bin/launcher` passed=`True` expected=`ad9fecfad3277d6467686a5743d86064103b1cd5409e50b21848360623f50b27` actual=`ad9fecfad3277d6467686a5743d86064103b1cd5409e50b21848360623f50b27`
- `bin/server` passed=`True` expected=`fc68dcf24ba122bec867ff75ed67328162f20faab119681ff21c082d506bc5e1` actual=`fc68dcf24ba122bec867ff75ed67328162f20faab119681ff21c082d506bc5e1`
- `bin/setup` passed=`True` expected=`a06bae4e9613042538d64604901e5367e84b733cc1987df2f276002769e074d9` actual=`a06bae4e9613042538d64604901e5367e84b733cc1987df2f276002769e074d9`

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
- `warn.trust.signature_missing` `signatures`: artifact is unsigned but the selected trust policy allows it
