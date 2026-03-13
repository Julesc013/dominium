Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-4 platform clean-room matrix

# Clean Room - win64

- result: `complete`
- source_bundle_root: `build/tmp/dist3_bundle_c/v0.0.0-mock/win64/dominium`
- seed: `456`
- mode_policy: `cli`
- deterministic_fingerprint: `b57061ccde8d12400a48bb6967b97ed66aacabac2c2b6324f0c1f5c3d2654e83`

## Assertions

- `exit_codes_all_success`: `True`
- `negotiation_records_present`: `True`
- `no_external_absolute_paths`: `True`
- `pack_verification_passed`: `True`
- `portable_root_detected`: `True`
- `replay_validates_determinism`: `True`
- `teleport_chain_complete`: `True`
- `tool_session_complete`: `True`
- `virtual_paths_within_bundle`: `True`

## Steps

- `setup_install_status` returncode=`0` result=`complete` payload_fingerprint=`b9609c4b770ee83f16046a2ed96aa8042e06a6eb2765c3fed07c827e00ccb1e4`
- `vpath_probe` returncode=`0` result=`complete` payload_fingerprint=`545edd6e2b4cf32f0d242f90afff6376b1a31df7d41e040c1cb0ffc51cc03f9e`
- `setup_verify` returncode=`0` result=`complete` payload_fingerprint=`fcd28cc87e510a20ac141533d5331ace621c43cc1a8f7804d57cda6393d922e4`
- `launcher_instances_list` returncode=`0` result=`complete` payload_fingerprint=`6f3bfa653520da8a39cbcc46b53139239df99b85e2b8903793dc59b71124883e`
- `launcher_compat_status` returncode=`0` result=`complete` payload_fingerprint=`67e7075396a328229504ddec82f397858dadf394b26007730592c1646a639d70`
- `launcher_start` returncode=`0` result=`complete` payload_fingerprint=`a1b75dca03cd63af291905826113091b196b777c2304bd29029859e931aff04e`
- `launcher_status` returncode=`0` result=`complete` payload_fingerprint=`c4efae54d0f5534a6badc196fe1d018b4ddb9bf4ffe1534427d4ff99f86c3b24`
- `launcher_attach_all` returncode=`0` result=`complete` payload_fingerprint=`aec647c851ea349d1d00430e0943767929aef4d0a177aced0365a6adfc1eae14`
- `teleport_chain` returncode=`0` result=`complete` payload_fingerprint=`b135094cb38e971afbfb0a8b9682b969197e5b7f22d4d5f0ed58d423259bf9ce`
- `tool_session` returncode=`0` result=`` payload_fingerprint=`ca0381d83379f41eb39c699544058a293b2bbba4afdf70fe2f9ec7d11885a270`
- `diag_capture` returncode=`0` result=`complete` payload_fingerprint=`254159d90ca7c090c6042eaea94ee8ef4292db79f1293be9994543237a8010d1`
- `replay_verify` returncode=`0` result=`complete` payload_fingerprint=`ae48e98d37f3d8bf9c72d8a5eb01b30500574dad7fad6833f7d46b19ba4ae216`
- `launcher_stop` returncode=`0` result=`complete` payload_fingerprint=`7262f8d9fd746cf8a7fef4b48442431ab08e06bc6fbcd26297b36874bb92c5f8`

## Key Hashes

- `diag_bundle_hash`: `4a638b5ef05540002b0e4eb1cc3224897f45a16da821a2163bcab1be459d96e0`
- `replay_bundle_hash`: `4a638b5ef05540002b0e4eb1cc3224897f45a16da821a2163bcab1be459d96e0`
- `replay_result_fingerprint`: `38aab8a5d484c3d5549456521dbc2d0543b6a29d8103d20ec68a5bf2206843e9`
- `teleport_chain_fingerprint`: `5618eaa051d816f8b2d4fb09d0f1ca6c0c7c40e250323f02c2965ef715c0d28a`
- `tool_session_fingerprint`: `44983b71853e6ec84ad19280d7e12816a66ffcd414a1fee6811a65c12cb6b5f2`

## Errors

- none

## Warnings

- none
