Status: Quarantine
Last Reviewed: 2026-03-26
Stability: provisional
Replacement Target: XI-4b manual review resolution

# Quarantine Packet `duplicate.sig.426a946a77a67082`

- Symbol: `load_product_capability_defaults`
- Cluster Kind: `exact`
- Cluster Resolution: `quarantine`
- Risk Level: `HIGH`
- Canonical Candidate: `src/compat/descriptor/__init__.py`
- Quarantine Reasons: `planned_quarantine`
- Planned Action Kinds: `quarantine`

## Competing Files

- `src/compat/descriptor/__init__.py`
- `src/compat/descriptor/descriptor_engine.py`
- `src/release/build_id_engine.py`

## Scorecard

- `src/compat/descriptor/__init__.py` disposition=`canonical` rank=`1` total_score=`65.54` risk=`HIGH`
- `src/compat/descriptor/descriptor_engine.py` disposition=`quarantine` rank=`2` total_score=`56.49` risk=`HIGH`
- `src/release/build_id_engine.py` disposition=`quarantine` rank=`3` total_score=`56.26` risk=`HIGH`

## Usage Sites

- Build Targets: `none`
- Docs: `docs/appshell/TUI_FRAMEWORK.md, docs/architecture/CANON_INDEX.md, docs/architecture/GLOSSARY.md, docs/architecture/SCHEMA_CHANGE_NOTES.md, docs/audit/APPSHELL3_RETRO_AUDIT.md, docs/audit/APPSHELL_TUI_BASELINE.md, docs/audit/CANON_MAP.md, docs/audit/CAP_NEG1_RETRO_AUDIT.md`

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
