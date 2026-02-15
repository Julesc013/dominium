Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Bound to `tools/xstack/testx/runner.py` and `tools/xstack/testx/tests/`.

# TestX Tool Harness

Purpose:
- Deterministic tool-suite test execution with FAST/STRICT/FULL selection, sharding, and cache.

Key files:
- `tools/xstack/testx/runner.py`
- `tools/xstack/testx/tests/test_*.py`

Invocation:
- `python tools/xstack/testx/runner.py --repo-root . --profile FAST`
- `python tools/xstack/testx/runner.py --repo-root . --profile FULL --shards 2 --shard-index 1`
- `python tools/xstack/testx_all.py --repo-root . --subset testx.session.boot,testx.lockfile.validate`

Selection notes:
- FAST uses deterministic impact-graph subset selection by default.
- If impact graph coverage is incomplete, FAST falls back to full suite safely (non-silent).
