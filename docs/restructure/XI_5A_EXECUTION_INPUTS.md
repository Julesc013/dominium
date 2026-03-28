Status: DERIVED
Last Reviewed: 2026-03-28
Stability: provisional
Future Series: XI
Replacement Target: XI-5a-v3 execution log and final audit report

# XI-5a Execution Inputs

- approved lock: `data/restructure/src_domain_mapping_lock_approved_v4.json`
- readiness contract: `data/restructure/xi5_readiness_contract_v4.json`
- dangerous shadow roots: `src/`, `app/src/`
- approved dangerous-shadow rows: `542`
- approved attic rows in this phase: `0`
- deferred rows left for later phases: `253`
- path derivation policy: `forbidden`

Xi-5a-v3 must move only rows listed in the v4 lock, must not touch legacy/source or component-local src rows, and must inherit the reserved-package protections already established for `platform` and `time`.
