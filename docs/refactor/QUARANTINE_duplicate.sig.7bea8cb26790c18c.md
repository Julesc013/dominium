Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.7bea8cb26790c18c`

- Symbol: `_file_text`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/release/ui_mode_resolution_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `tools/auditx/analyzers/e231_undeclared_temporal_domain_smell.py`
- `tools/auditx/analyzers/e531_secrets_in_log_smell.py`
- `tools/governance/governance_model_common.py`
- `tools/meta/observability_common.py`
- `tools/release/platform_formalize_common.py`
- `tools/release/ui_mode_resolution_common.py`
- `tools/release/ui_reconcile_common.py`
- `tools/security/trust_model_common.py`
- `tools/xstack/repox/check.py`

## Scorecard

- `tools/release/ui_mode_resolution_common.py` disposition=`canonical` rank=`1` total_score=`86.43` risk=`HIGH`
- `tools/meta/observability_common.py` disposition=`quarantine` rank=`2` total_score=`84.29` risk=`HIGH`
- `tools/security/trust_model_common.py` disposition=`merge` rank=`3` total_score=`83.16` risk=`HIGH`
- `tools/governance/governance_model_common.py` disposition=`merge` rank=`4` total_score=`82.5` risk=`HIGH`
- `tools/release/ui_reconcile_common.py` disposition=`merge` rank=`5` total_score=`71.08` risk=`HIGH`
- `tools/release/platform_formalize_common.py` disposition=`merge` rank=`6` total_score=`67.45` risk=`HIGH`
- `tools/auditx/analyzers/e231_undeclared_temporal_domain_smell.py` disposition=`drop` rank=`7` total_score=`66.58` risk=`HIGH`
- `tools/xstack/repox/check.py` disposition=`drop` rank=`8` total_score=`66.07` risk=`HIGH`
- `tools/auditx/analyzers/e531_secrets_in_log_smell.py` disposition=`drop` rank=`9` total_score=`59.3` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/GLOSSARY.md, docs/appshell/UI_MODE_RESOLUTION.md, docs/appshell/VIRTUAL_PATHS.md, docs/architecture/BEHAVIORAL_COMPONENTS_STANDARD.md, docs/architecture/CANON_INDEX.md, docs/architecture/COLLAPSE_EXPAND_SOLVERS.md, docs/architecture/COMPLEXITY_AND_SCALE.md, docs/architecture/CONTROL_LAYERS.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/security/tool_run_trust_strict_suite.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
