Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5 bounded execution against approved mapping lock

# XI-4Z Fix Report

## Outcome

- Canonical approved lock: `data/restructure/src_domain_mapping_lock_approved.json`
- Canonical readiness contract: `data/restructure/xi5_readiness_contract.json`
- Files changed: `16`
- Scratch files updated: `2`
- Mapping decisions changed: `no`
- Remaining mismatches: `0`

## Repairs

| File | Inconsistency | Old | New |
| --- | --- | --- | --- |
| `docs/restructure/XI_4Z_XI5_READINESS.md` | `bare_readiness_contract_reference` | `constrained by xi5_readiness_contract.json` | `constrained by data/restructure/xi5_readiness_contract.json` |
| `docs/restructure/XI_4Z_DECISION_REPORT.md` | `missing_explicit_approved_lock_reference` | `missing` | `data/restructure/src_domain_mapping_lock_approved.json` |
| `docs/restructure/XI_4Z_DECISION_REPORT.md` | `missing_explicit_readiness_contract_reference` | `missing` | `data/restructure/xi5_readiness_contract.json` |
| `docs/audit/XI_4Z_FINAL.md` | `bare_lock_and_contract_reference` | `when constrained by xi5_readiness_contract.json and src_domain_mapping_lock_approved.json` | `when constrained by data/restructure/xi5_readiness_contract.json and data/restructure/src_domain_mapping_lock_approved.json` |
| `data/restructure/xi4z_decision_manifest.json` | `missing_readiness_contract_path_field` | `missing` | `data/restructure/xi5_readiness_contract.json` |
| `tmp/xi4z_xi5_readiness_bundle_manifest.txt` | `bundle_manifest_refreshed` | `stale XI-4z bundle manifest metadata` | `refreshed to canonical XI-4z bundle entry set` |

## Validation

- Authoritative files exist: `yes`
- Xi-4z reports reference canonical files: `yes`
- Xi-5a helper tooling reference status: `none_detected`
- Deterministic rerun match: `yes`

