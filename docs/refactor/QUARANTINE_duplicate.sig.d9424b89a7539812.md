Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.d9424b89a7539812`

- Symbol: `normalize_entropy_state_rows`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/physics/entropy/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/physics/__init__.py`
- `src/physics/entropy/__init__.py`
- `src/physics/entropy/entropy_engine.py`

## Scorecard

- `src/physics/entropy/__init__.py` disposition=`canonical` rank=`1` total_score=`75.3` risk=`HIGH`
- `src/physics/__init__.py` disposition=`merge` rank=`2` total_score=`75.0` risk=`HIGH`
- `src/physics/entropy/entropy_engine.py` disposition=`quarantine` rank=`3` total_score=`73.87` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/architecture/ANTI_ENTROPY_RULES.md, docs/architecture/ARCH_CHANGE_PROCESS.md, docs/architecture/CANON_INDEX.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/LAW_AND_META_LAW.md, docs/architecture/RNG_MODEL.md, docs/audit/CANON_MAP.md, docs/audit/CHEM1_RETRO_AUDIT.md`

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

- Review file-local deltas and port only unique behavior into the canonical file.
- Rewire call sites only after confirming the secondary file is not an active product entrypoint.
- Deprecate the secondary file only after it is removed from default build targets and no longer carries unrelated active symbols.
- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
