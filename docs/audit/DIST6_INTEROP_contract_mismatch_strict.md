Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - contract_mismatch_strict

- case_label: `Contract mismatch with strict refusal`
- result: `complete`
- deterministic_fingerprint: `5a7fc82c5d3ab21dca6008a9bcd2f19adeac61c9b33447c8a4d4856298ce5d1c`

## Bundles

- bundle_a: `win64` `build/tmp/dist6_interop_a/v0.0.0-mock/win64/dominium` source=`built`
- bundle_b: `win64` `build/tmp/dist6_interop_b/v0.0.0-mock/win64/dominium` source=`built`

## Negotiation

- result: `refused`
- compatibility_mode_id: `compat.refuse`
- refusal_code: `refusal.compat.contract_mismatch`
- negotiation_record_hash: `643eb53bea92a863b60d482deaf7cc246731fda6e5e9e3a66ed696cfedf2116f`
- chosen_protocol: `protocol.loopback.session` `1.0.0`

## Surfaces

- `server` returncode=`30` mode=`none` refusal=`refusal.compat.contract_mismatch` events=`appshell.bootstrap.start, appshell.paths.initialized, compat.install_selected, appshell.mode.selected, appshell.command.dispatch, compat.negotiation.refused, appshell.refusal`

## Save Compatibility

- result=`refused` refusal=`refusal.save.contract_mismatch` read_only_required=`False` degrade_reasons=`none`

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `negotiation_record_present`: `True`
- `save_behavior_matched`: `True`

## Notes

- strict mode must refuse both endpoint interop and save-open drift without silent fallback

## Errors

- none
