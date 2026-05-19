Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - contract_mismatch_read_only

- case_label: `Contract mismatch with read-only fallback`
- result: `complete`
- deterministic_fingerprint: `6bb2ea1d1a8e22582ee761377b7c2f3f5a17778edaf1536deb0f2db7ce6e8cd1`

## Bundles

- bundle_a: `win64` `build/tmp/dist6_interop_a/v0.0.0-mock/win64/dominium` source=`built`
- bundle_b: `win64` `build/tmp/dist6_interop_b/v0.0.0-mock/win64/dominium` source=`built`

## Negotiation

- result: `complete`
- compatibility_mode_id: `compat.read_only`
- refusal_code: `none`
- negotiation_record_hash: `93ac1b6f3455a53c108fe1a071557eb3c5b8ea5a3236bf34668cfb5811aaa692`
- chosen_protocol: `protocol.loopback.session` `1.0.0`

## Surfaces

- `server` returncode=`0` mode=`compat.read_only` refusal=`none` events=`appshell.bootstrap.start, appshell.paths.initialized, compat.install_selected, appshell.mode.selected, appshell.command.dispatch, compat.negotiation.result`

## Save Compatibility

- result=`complete` refusal=`none` read_only_required=`True` degrade_reasons=`save_contract_bundle_mismatch`

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `negotiation_record_present`: `True`
- `save_behavior_matched`: `True`

## Notes

- read-only fallback must be explicit in both negotiation output and save-open evaluation

## Errors

- none
