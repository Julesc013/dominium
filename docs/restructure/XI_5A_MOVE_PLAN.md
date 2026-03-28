Status: DERIVED
Last Reviewed: 2026-03-28
Stability: provisional
Future Series: XI-5
Replacement Target: XI-5a execution log and final audit report

# XI-5A Move Plan

- approved lock: `data/restructure/src_domain_mapping_lock_approved_v4.json`
- readiness contract: `data/restructure/xi5_readiness_contract_v4.json`
- batching model: single deterministic dangerous-shadow batch
  reason: the approved Python move surface has cross-package import coupling, so partial category batches would introduce transient import breakage unrelated to the approved lock.
- approved moves in this pass: `542`
- approved attic routes in this pass: `0`
- deferred rows left untouched: `253`

## Deferred Dangerous-Root Residuals
- `src/worldgen/__init__.py` remains deferred because `Approved row cannot execute mechanically without overwriting an existing active file, so it is deferred to XI-5b.`
