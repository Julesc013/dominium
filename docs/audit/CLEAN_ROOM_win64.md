Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-4 platform clean-room matrix

# Clean Room - win64

- result: `complete`
- source_bundle_root: `dist/v0.0.0-mock/win64/dominium`
- seed: `456`
- mode_policy: `cli`
- deterministic_fingerprint: `f9715b489dcd45d9e0642b75e85e77c69adc0ae87d7525413e7c63d0cc97dbc6`

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

- `setup_install_status` returncode=`0` result=`complete` payload_fingerprint=`ad00fa5d95519d04eb4790aa12409f40ef94cc5f4e579d01b63679d5e60ac835`
- `vpath_probe` returncode=`0` result=`complete` payload_fingerprint=`50f8a7d8b447ba859600c88fb3ee9d11907785367770001332aa21fb8124e1c9`
- `setup_verify` returncode=`0` result=`complete` payload_fingerprint=`3f3347584dab51fcacdaf195798e37ebda9eff21e59d705a11cacf5556267ea8`
- `launcher_instances_list` returncode=`0` result=`complete` payload_fingerprint=`28e910fff51b2e6168a001fcf363a26e92072fb532a416cea5fb0e00289cb424`
- `launcher_compat_status` returncode=`0` result=`complete` payload_fingerprint=`e6d29262a6441d308471735d3f24333e78328933331b531c1583bcfc0672dcbf`
- `launcher_start` returncode=`0` result=`complete` payload_fingerprint=`52d85b5e9ba74bc603638ef791c3dd452ec4a83992db8ec284eb0c11b7cf4ba2`
- `launcher_status` returncode=`0` result=`complete` payload_fingerprint=`4ac8a3ba5efe68018096a9e3ca8e15c80edc8dd99bae26ea3743b0f6e7aa604a`
- `launcher_attach_all` returncode=`0` result=`complete` payload_fingerprint=`7328af92295fe57b286378a757ef816c12502ea5f17942a4d54e9fa395d1dbb9`
- `teleport_chain` returncode=`0` result=`complete` payload_fingerprint=`f7a430c9f04ee91e702d99801d64feaf810670ace32b1b0f9b499d8d00885dbc`
- `tool_session` returncode=`0` result=`` payload_fingerprint=`4b52f9da6b4dd6e908e31dc466d44f1a434a2f9a8a7da614bdee425e7baaa9d4`
- `diag_capture` returncode=`0` result=`complete` payload_fingerprint=`be5b698fd3832625748d69c33f470cf0742ca716ef9f679cf1f7b5712ac5ba93`
- `replay_verify` returncode=`0` result=`complete` payload_fingerprint=`af2d4618a658ef915acee89d3fc88f051d147c222a9c856d52bc1f1e9d376025`
- `launcher_stop` returncode=`0` result=`complete` payload_fingerprint=`cd5a20fbca9a532167a3bddc55d9d310546200fd0abe08e292d401f32a96648c`

## Key Hashes

- `diag_bundle_hash`: `9fba85cacbc22e05a5d9152f0d2eff4c885ae9a716d369a8a4a870823c09a9f1`
- `replay_bundle_hash`: `9fba85cacbc22e05a5d9152f0d2eff4c885ae9a716d369a8a4a870823c09a9f1`
- `replay_result_fingerprint`: `859c59f02cf99023e6a163e7fc294a273caa5fef30894dadf2fc2707061f8c1a`
- `teleport_chain_fingerprint`: `6ee06c5694783266760b12c62c27c61c452f5d1c092107b35bcbc41ef26904f3`
- `tool_session_fingerprint`: `3dfa6290a3f878fe5ff50f0e1f961b95787c1be8486ed59e48ec2869f2ad810e`

## Errors

- none

## Warnings

- none
