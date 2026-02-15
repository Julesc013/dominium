Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Bound to canon/glossary deprecated-term rules and `tools/xstack/run.py`.

# RepoX Minimal

Purpose:
- Deterministic forbidden-pattern and mode-flag heuristic scan for tooling surfaces.

Key file:
- `tools/xstack/repox/check.py`

Invocation:
- `python tools/xstack/repox/check.py --repo-root . --profile FAST`

STRICT/FULL renderer boundary rules:
- `repox.renderer_truth_import`
- `repox.renderer_truth_symbol`
