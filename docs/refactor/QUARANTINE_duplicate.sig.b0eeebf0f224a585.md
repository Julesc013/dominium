Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b0eeebf0f224a585`

- Symbol: `_iter_candidate_files`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/auditx/analyzers/e334_adhoc_spatial_key_smell.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `deprecate, quarantine`

## Competing Files

- `tools/auditx/analyzers/e334_adhoc_spatial_key_smell.py`
- `tools/auditx/analyzers/e335_nondeterministic_local_index_smell.py`
- `tools/auditx/analyzers/e336_raw_global_coord_smell.py`
- `tools/auditx/analyzers/e338_raw_sqrt_usage_smell.py`
- `tools/auditx/analyzers/e339_hardcoded_distance_smell.py`
- `tools/auditx/analyzers/e348_unnamed_rng_worldgen_smell.py`
- `tools/auditx/analyzers/e350_silent_identity_change_smell.py`
- `tools/auditx/analyzers/e351_nondeterministic_merge_smell.py`
- `tools/auditx/analyzers/e352_nondeterministic_distance_smell.py`

## Scorecard

- `tools/auditx/analyzers/e334_adhoc_spatial_key_smell.py` disposition=`canonical` rank=`1` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e336_raw_global_coord_smell.py` disposition=`quarantine` rank=`2` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e338_raw_sqrt_usage_smell.py` disposition=`quarantine` rank=`3` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e339_hardcoded_distance_smell.py` disposition=`quarantine` rank=`4` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e350_silent_identity_change_smell.py` disposition=`quarantine` rank=`5` total_score=`56.55` risk=`HIGH`
- `tools/auditx/analyzers/e348_unnamed_rng_worldgen_smell.py` disposition=`drop` rank=`6` total_score=`37.98` risk=`HIGH`
- `tools/auditx/analyzers/e335_nondeterministic_local_index_smell.py` disposition=`drop` rank=`7` total_score=`35.12` risk=`HIGH`
- `tools/auditx/analyzers/e351_nondeterministic_merge_smell.py` disposition=`drop` rank=`8` total_score=`35.12` risk=`HIGH`
- `tools/auditx/analyzers/e352_nondeterministic_distance_smell.py` disposition=`drop` rank=`9` total_score=`35.12` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `none`

## Tests Involved

- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
