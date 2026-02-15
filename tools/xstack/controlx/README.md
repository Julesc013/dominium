Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Bound to `tools/xstack/run.py` and canon/glossary v1.0.0.

# ControlX

Purpose:
- Deterministic orchestration for `FAST`, `STRICT`, and `FULL` XStack profiles.

Key files:
- `tools/xstack/controlx/orchestrator.py`
- `tools/xstack/controlx/types.py`
- `tools/xstack/controlx/utils.py`

Invocation:
- `tools/xstack/run fast`
- `tools/xstack/run strict`
- `tools/xstack/run full --shards 2 --shard-index 0`

