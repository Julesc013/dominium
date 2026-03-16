Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DIST
Replacement Target: DIST-7 packaging artifacts and signed release archive validation

# DIST6 Final

- result: `complete`
- case_ids: `contract_mismatch_read_only, contract_mismatch_strict, minor_protocol_drift, pack_lock_mismatch, same_build_identical_rebuild, same_build_same_build, same_version_cross_platform`
- failure_count: `0`
- deterministic_fingerprint: `c19daeccb52e02aef1e303646f0ffa1cd6bf14e1e1da3cdafee48048c2ae46f7`

## Matrix Summary

- `contract_mismatch_read_only` result=`complete` mode=`compat.read_only` refusal=`none` hash=`93ac1b6f3455a53c108fe1a071557eb3c5b8ea5a3236bf34668cfb5811aaa692`
- `contract_mismatch_strict` result=`complete` mode=`compat.refuse` refusal=`refusal.compat.contract_mismatch` hash=`643eb53bea92a863b60d482deaf7cc246731fda6e5e9e3a66ed696cfedf2116f`
- `minor_protocol_drift` result=`complete` mode=`compat.degraded` refusal=`none` hash=`f439ed76bcbeed68d62d32e15882ee5f8a77752c1ccce7f93239565f9bab7aec`
- `pack_lock_mismatch` result=`complete` mode=`compat.degraded` refusal=`refusal.save.pack_lock_mismatch` hash=`03983ebd8753ad1937138c31f90cb0058755d112250fcb4f798a19b87a482b73`
- `same_build_identical_rebuild` result=`complete` mode=`compat.degraded` refusal=`none` hash=`03983ebd8753ad1937138c31f90cb0058755d112250fcb4f798a19b87a482b73`
- `same_build_same_build` result=`complete` mode=`compat.degraded` refusal=`none` hash=`03983ebd8753ad1937138c31f90cb0058755d112250fcb4f798a19b87a482b73`
- `same_version_cross_platform` result=`complete` mode=`compat.degraded` refusal=`none` hash=`f7a1d1743a7bac1ef8f6fce1878bf5293cd2059d7a1626e957809679e3b1bd1b`

## Refusal And Degrade Cases

- `contract_mismatch_read_only` compat=`compat.read_only` compat_refusal=`none` save_refusal=`none` degrade_reasons=`save_contract_bundle_mismatch`
- `contract_mismatch_strict` compat=`compat.refuse` compat_refusal=`refusal.compat.contract_mismatch` save_refusal=`refusal.save.contract_mismatch` degrade_reasons=`none`
- `minor_protocol_drift` compat=`compat.degraded` compat_refusal=`none` save_refusal=`none` degrade_reasons=`none`
- `pack_lock_mismatch` compat=`compat.degraded` compat_refusal=`none` save_refusal=`refusal.save.pack_lock_mismatch` degrade_reasons=`none`
- `same_build_identical_rebuild` compat=`compat.degraded` compat_refusal=`none` save_refusal=`none` degrade_reasons=`none`
- `same_build_same_build` compat=`compat.degraded` compat_refusal=`none` save_refusal=`none` degrade_reasons=`none`
- `same_version_cross_platform` compat=`compat.degraded` compat_refusal=`none` save_refusal=`none` degrade_reasons=`none`

## Readiness

- DIST-7 packaging artifacts: ready
