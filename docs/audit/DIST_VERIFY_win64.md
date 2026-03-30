Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-3 clean-room distribution verification baseline

# DIST Verify - win64

- result: `complete`
- bundle_root: `dist/v0.0.0-mock/win64/dominium`
- deterministic_fingerprint: `0693d807a43fba8611bc57fd48bf3ae92476b95e6bbce385f9cab4acd1e44b20`

## Layout Check

- result: `complete`
- missing_paths: `none`

## Release Manifest Verification

- result: `complete`
- verified_artifact_count: `25`
- manifest_hash: `d5d2707f0a8911f4f24577f0b0a9cd4c5200ac9a6a637f4ba73d3edf56706ad5`

## Pack Verification

- result: `complete`
- returncode: `0`

## Descriptor Checks

- `bin/client` passed=`True` expected=`9790432e5c8a3bc4f628ad62cd5c0be2ef985f94555c7b942066aee4965aa3c0` actual=`9790432e5c8a3bc4f628ad62cd5c0be2ef985f94555c7b942066aee4965aa3c0`
- `bin/engine` passed=`True` expected=`3b897a91915587d4719a09bcf75288ca27013654d6a644df57c51e1e85e46f37` actual=`3b897a91915587d4719a09bcf75288ca27013654d6a644df57c51e1e85e46f37`
- `bin/game` passed=`True` expected=`0db61e9a0dfa17c5c6593aa924e5a127bf9d55fdb8f9e812fff31282561a1807` actual=`0db61e9a0dfa17c5c6593aa924e5a127bf9d55fdb8f9e812fff31282561a1807`
- `bin/launcher` passed=`True` expected=`5a1ba8869c91ed3dc7a4c2151f1eecd7935289a7a7ff88dbd4d0081bbb84d4f6` actual=`5a1ba8869c91ed3dc7a4c2151f1eecd7935289a7a7ff88dbd4d0081bbb84d4f6`
- `bin/server` passed=`True` expected=`45eac3a7505045c0b29d6f4152957abe2a9284763f1579e5a3672c37025c2a07` actual=`45eac3a7505045c0b29d6f4152957abe2a9284763f1579e5a3672c37025c2a07`
- `bin/setup` passed=`True` expected=`3dcdcd2df0d861899cedb1907597a2f1e3cf2cfc7b9523a5b6f8e395a2e2e7da` actual=`3dcdcd2df0d861899cedb1907597a2f1e3cf2cfc7b9523a5b6f8e395a2e2e7da`

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
