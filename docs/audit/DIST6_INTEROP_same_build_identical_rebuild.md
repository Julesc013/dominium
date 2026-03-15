Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 archive packaging and signed release interop notes

# DIST6 Interop - same_build_identical_rebuild

- case_label: `Same build ↔ rebuilt identical build`
- result: `complete`
- deterministic_fingerprint: `c573c99a66420548642b9fa2863f3bd1baabdc5138eff4a5f9ed129144bb6fb5`

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

- `client` returncode=`0` mode=`compat.degraded` refusal=`none` events=`appshell.bootstrap.start, appshell.paths.initialized, compat.install_selected, appshell.mode.selected, appshell.command.dispatch, compat.negotiation.result`

## Save Compatibility

- none

## Assertions

- `degrade_logged`: `True`
- `expected_mode_observed`: `True`
- `identical_rebuild_hash_match`: `True`
- `negotiation_record_present`: `True`
- `same_build_id`: `True`
- `save_behavior_matched`: `True`

## Notes

- bundle B is rebuilt from identical inputs and is expected to keep the same build_id and negotiation hash

## Errors

- none
