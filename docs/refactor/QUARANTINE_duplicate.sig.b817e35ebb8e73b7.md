Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.b817e35ebb8e73b7`

- Symbol: `field_type_rows_by_id`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/fields/__init__.py`
- Quarantine Reasons: `phase_boundary_deferred, planned_quarantine, requires_single_action_full_gate`
- Planned Action Kinds: `merge, rewire, deprecate, quarantine`

## Competing Files

- `src/field/__init__.py`
- `src/fields/__init__.py`
- `src/fields/field_engine.py`

## Scorecard

- `src/fields/__init__.py` disposition=`canonical` rank=`1` total_score=`77.62` risk=`HIGH`
- `src/field/__init__.py` disposition=`quarantine` rank=`2` total_score=`73.27` risk=`HIGH`
- `src/fields/field_engine.py` disposition=`merge` rank=`3` total_score=`70.89` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/SCHEMA_CANON_ALIGNMENT.md, docs/architecture/HAZARDS_MODEL.md, docs/architecture/RISK_AND_LIABILITY_MODEL.md, docs/architecture/SEMANTIC_STABILITY_POLICY.md, docs/architecture/SIGNAL_MODEL.md, docs/architecture/TERRAIN_FIELDS.md, docs/architecture/TERRAIN_PROVIDER_CHAIN.md, docs/architecture/TERRAIN_TRUTH_MODEL.md`

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
