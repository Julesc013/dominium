Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.6e9d727fedd1264f`

- Symbol: `REFUSAL_PROCESS_CAPSULE_OUT_OF_DOMAIN`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/process/capsules/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/process/__init__.py`
- `src/process/capsules/__init__.py`
- `src/process/capsules/capsule_executor.py`

## Scorecard

- `src/process/capsules/__init__.py` disposition=`canonical` rank=`1` total_score=`63.87` risk=`HIGH`
- `src/process/capsules/capsule_executor.py` disposition=`quarantine` rank=`2` total_score=`56.13` risk=`HIGH`
- `src/process/__init__.py` disposition=`quarantine` rank=`3` total_score=`55.6` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/CANON_INDEX.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md, docs/audit/LOGIC_CONSTITUTION_BASELINE.md, docs/audit/META_STABILITY0_RETRO_AUDIT.md, docs/audit/MODULE_DUPLICATION_REPORT.md, docs/audit/PROCESS_CAPSULE_BASELINE.md, docs/audit/PROCESS_DEFINITION_BASELINE.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
