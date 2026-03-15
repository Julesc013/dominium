Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - same_version_cross_platform

- case_label: `Same version, different platform tag`
- result: `complete`
- deterministic_fingerprint: `0262c7814736d5fb91c92efe66f59658d1538bc4a19d7c930b73533206e6efd7`

## Bundles

- bundle_a: `win64` `build/tmp/dist6_interop_a/v0.0.0-mock/win64/dominium` source=`built`
- bundle_b: `win64` `build/tmp/dist6_interop_b/v0.0.0-mock/win64/dominium` source=`built`

## Negotiation

- result: `complete`
- compatibility_mode_id: `compat.degraded`
- refusal_code: `none`
- negotiation_record_hash: `f7a1d1743a7bac1ef8f6fce1878bf5293cd2059d7a1626e957809679e3b1bd1b`
- chosen_protocol: `protocol.loopback.session` `1.0.0`

## Surfaces

- none

## Save Compatibility

- none

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `negotiation_record_present`: `True`
- `save_behavior_matched`: `True`

## Notes

- cross-platform case uses a deterministic projected platform descriptor when no second built platform bundle is available

## Errors

- none
