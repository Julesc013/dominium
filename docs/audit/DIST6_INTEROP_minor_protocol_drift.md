Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - minor_protocol_drift

- case_label: `Minor protocol drift with overlapping range`
- result: `complete`
- deterministic_fingerprint: `605d59a32d3fe7d14a8a3a0ccefcb775b8650402fa53bb5b282c37b9de67df62`

## Bundles

- bundle_a: `win64` `build/tmp/dist6_interop_a/v0.0.0-mock/win64/dominium` source=`built`
- bundle_b: `win64` `build/tmp/dist6_interop_b/v0.0.0-mock/win64/dominium` source=`built`

## Negotiation

- result: `complete`
- compatibility_mode_id: `compat.degraded`
- refusal_code: `none`
- negotiation_record_hash: `f439ed76bcbeed68d62d32e15882ee5f8a77752c1ccce7f93239565f9bab7aec`
- chosen_protocol: `protocol.loopback.session` `1.0.0`

## Surfaces

- `server` returncode=`0` mode=`compat.degraded` refusal=`none` events=`appshell.bootstrap.start, appshell.paths.initialized, compat.install_selected, appshell.mode.selected, appshell.command.dispatch, compat.negotiation.result`

## Save Compatibility

- none

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `negotiation_record_present`: `True`
- `save_behavior_matched`: `True`

## Notes

- protocol overlap remains lawful and should select the stable shared loopback version

## Errors

- none
