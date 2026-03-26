Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.cluster.6d9d190b17a3643f`

- Symbol: `ARCHIVE_POLICY_ID`
- Cluster Kind: `near`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/governance/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/governance/__init__.py`
- `src/governance/governance_profile.py`

## Scorecard

- `src/governance/__init__.py` disposition=`canonical` rank=`1` total_score=`69.52` risk=`HIGH`
- `src/governance/governance_profile.py` disposition=`quarantine` rank=`2` total_score=`64.34` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/SURVIVAL_SLICE.md, docs/agents/AGENT_POWER.md, docs/architecture/ARCH0_CONSTITUTION.md, docs/architecture/CANON_INDEX.md, docs/architecture/CIVILIZATION_MODEL.md, docs/architecture/CONTRACTS_INDEX.md, docs/architecture/EXTENSION_MAP.md, docs/architecture/GOVERNANCE_AND_INSTITUTIONS.md`

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
