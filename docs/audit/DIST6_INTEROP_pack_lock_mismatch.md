Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - pack_lock_mismatch

- case_label: `Pack lock mismatch`
- result: `complete`
- deterministic_fingerprint: `f3aa51daaced95524b374bf60ea5a5bacf07b9f214b7a81888864d3425e72138`

## Bundles

- bundle_a: `win64` `build/tmp/dist6_interop_a/v0.0.0-mock/win64/dominium` source=`built`
- bundle_b: `win64` `build/tmp/dist6_interop_b/v0.0.0-mock/win64/dominium` source=`built`

## Negotiation

- result: `complete`
- compatibility_mode_id: `compat.degraded`
- refusal_code: `none`
- negotiation_record_hash: `03983ebd8753ad1937138c31f90cb0058755d112250fcb4f798a19b87a482b73`
- chosen_protocol: `protocol.loopback.session` `1.0.0`

## Surfaces

- none

## Save Compatibility

- result=`refused` refusal=`refusal.save.pack_lock_mismatch` read_only_required=`False` degrade_reasons=`none`

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `negotiation_record_present`: `True`
- `save_behavior_matched`: `True`

## Notes

- pack mismatch is refused deterministically even when endpoint negotiation remains lawful

## Errors

- none
