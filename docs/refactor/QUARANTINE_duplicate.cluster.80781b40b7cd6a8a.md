Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.80781b40b7cd6a8a`

- Symbol: `REPORT_JSON_REL`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `tools/meta/identity_common.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `tools/compat/migration_lifecycle_common.py`
- `tools/meta/identity_common.py`
- `tools/release/arch_matrix_common.py`
- `tools/release/install_profile_common.py`
- `tools/release/update_model_common.py`

## Scorecard

- `tools/meta/identity_common.py` disposition=`canonical` rank=`1` total_score=`87.38` risk=`HIGH`
- `tools/release/install_profile_common.py` disposition=`quarantine` rank=`2` total_score=`85.36` risk=`HIGH`
- `tools/release/arch_matrix_common.py` disposition=`quarantine` rank=`3` total_score=`84.76` risk=`HIGH`
- `tools/compat/migration_lifecycle_common.py` disposition=`quarantine` rank=`4` total_score=`84.64` risk=`HIGH`
- `tools/release/update_model_common.py` disposition=`quarantine` rank=`5` total_score=`84.64` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/ARCHITECTURE.md, docs/GLOSSARY.md, docs/agents/AGENT_IDENTITY.md, docs/agents/AGENT_INSTITUTIONS.md, docs/agents/AGENT_LIFECYCLE.md, docs/agents/AGENT_MODEL.md, docs/agents/AGENT_NON_GOALS.md, docs/app/ARTIFACT_IDENTITY.md`

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
