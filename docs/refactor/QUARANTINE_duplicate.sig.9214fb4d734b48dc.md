Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.9214fb4d734b48dc`

- Symbol: `REFUSAL_DISPATCH_POLICY_FORBIDDEN`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/signals/institutions/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/signals/__init__.py`
- `src/signals/institutions/__init__.py`
- `src/signals/institutions/dispatch_engine.py`

## Scorecard

- `src/signals/institutions/__init__.py` disposition=`canonical` rank=`1` total_score=`64.52` risk=`HIGH`
- `src/signals/__init__.py` disposition=`quarantine` rank=`2` total_score=`58.1` risk=`HIGH`
- `src/signals/institutions/dispatch_engine.py` disposition=`merge` rank=`3` total_score=`51.17` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/agents/AGENT_MODEL.md, docs/architecture/CANON_INDEX.md, docs/architecture/EXTENSION_RULES.md, docs/architecture/INSTITUTIONS_AND_GOVERNANCE_MODEL.md, docs/architecture/WHY_ECONOMIES_DONT_FAKE.md, docs/archive/stray_root_docs/MODDING.md, docs/audit/CANON_MAP.md, docs/audit/DOC_INDEX.md`

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
