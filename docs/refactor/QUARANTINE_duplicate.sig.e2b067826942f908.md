Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.e2b067826942f908`

- Symbol: `_report_fingerprint`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/audit/arch_audit_common.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/validation/validation_engine.py`
- `tools/audit/arch_audit_common.py`
- `tools/time/time_anchor_common.py`

## Scorecard

- `tools/audit/arch_audit_common.py` disposition=`canonical` rank=`1` total_score=`66.07` risk=`HIGH`
- `tools/time/time_anchor_common.py` disposition=`quarantine` rank=`2` total_score=`66.07` risk=`HIGH`
- `src/validation/validation_engine.py` disposition=`merge` rank=`3` total_score=`50.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/CONTRIBUTING.md, docs/GLOSSARY.md, docs/architecture/ARCH_REPO_LAYOUT.md, docs/architecture/CANON_INDEX.md, docs/architecture/DEPRECATION_AND_QUARANTINE.md, docs/architecture/DUPLICATION_DETECTION_RULES.md, docs/architecture/REPO_NAV.md, docs/architecture/RETRO_CONSISTENCY_AUDIT_FRAMEWORK.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/time/tool_verify_longrun_ticks.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
