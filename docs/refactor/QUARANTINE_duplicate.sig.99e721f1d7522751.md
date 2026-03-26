Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.99e721f1d7522751`

- Symbol: `dg_type_registry_add`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `engine/modules/sim/pkt/registry/dg_type_registry.c`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `engine/modules/sim/pkt/registry/dg_type_registry.c`
- `engine/modules/sim/pkt/registry/dg_type_registry.h`

## Scorecard

- `engine/modules/sim/pkt/registry/dg_type_registry.c` disposition=`canonical` rank=`1` total_score=`88.69` risk=`HIGH`
- `engine/modules/sim/pkt/registry/dg_type_registry.h` disposition=`quarantine` rank=`2` total_score=`87.8` risk=`HIGH`

## Usage Sites

- Build Targets: `domino_core`
- Docs: `docs/SCHEMA_CANON_ALIGNMENT.md, docs/architecture/BUDGET_POLICY.md, docs/architecture/CORE_ABSTRACTIONS.md, docs/architecture/REGISTRY_PATTERN.md, docs/architecture/astronomy_catalogs.md, docs/architecture/deterministic_packaging.md, docs/architecture/fidelity_policy.md, docs/architecture/interest_regions.md`

## Tests Involved

- `python tools/compat/tool_run_interop_stress.py --repo-root .`
- `python tools/convergence/tool_run_convergence_gate.py --repo-root .`
- `python tools/mvp/tool_run_all_stress.py --repo-root .`
- `python tools/mvp/tool_run_disaster_suite.py --repo-root .`
- `python tools/mvp/tool_run_product_boot_matrix.py --repo-root .`
- `python tools/mvp/tool_verify_baseline_universe.py --repo-root .`
- `python tools/mvp/tool_verify_gameplay_loop.py --repo-root .`
- `python tools/validation/tool_run_validation.py --repo-root . --profile STRICT`
- `python tools/worldgen/tool_verify_worldgen_lock.py --repo-root .`
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_convergence_plan_deterministic,test_decision_rules_stable`

## Recommended Decision Options

- If ambiguity remains after review, keep the cluster quarantined for XI-4b instead of forcing convergence.
