"""Scoped authoritative paths for TIME-ANCHOR-0 enforcement."""

from __future__ import annotations


SCOPED_TIME_ANCHOR_PATHS: tuple[str, ...] = (
    "src/time/tick_t.py",
    "src/time/time_engine.py",
    "src/time/time_mapping_engine.py",
    "src/time/epoch_anchor_engine.py",
    "src/server/runtime/tick_loop.py",
    "src/server/server_console.py",
    "src/server/server_boot.py",
    "src/meta/provenance/compaction_engine.py",
    "tools/xstack/sessionx/script_runner.py",
    "tools/xstack/sessionx/time_lineage.py",
    "tools/server/server_mvp0_probe.py",
    "tools/time/tool_verify_longrun_ticks.py",
    "tools/time/tool_compaction_anchor_check.py",
)

REQUIRED_TIME_ANCHOR_FILES: tuple[str, ...] = (
    "docs/time/TIME_ANCHOR_MODEL.md",
    "docs/audit/TIME_ANCHOR0_RETRO_AUDIT.md",
    "schema/time/tick_t.schema",
    "schema/time/epoch_anchor_record.schema",
    "schemas/tick_t.schema.json",
    "schemas/epoch_anchor_record.schema.json",
    "data/registries/time_anchor_policy_registry.json",
    "src/time/tick_t.py",
    "src/time/epoch_anchor_engine.py",
    "tools/time/tool_verify_longrun_ticks.py",
    "tools/time/tool_compaction_anchor_check.py",
    "tools/xstack/testx/tests/test_epoch_anchor_emitted_on_interval.py",
    "tools/xstack/testx/tests/test_anchor_contains_required_hashes.py",
    "tools/xstack/testx/tests/test_compaction_respects_anchor_boundaries.py",
    "tools/xstack/testx/tests/test_tick_type_64bit_enforced.py",
    "tools/xstack/testx/tests/test_cross_platform_anchor_hash_match.py",
)

FORBIDDEN_TICK_WIDTH_TOKENS: tuple[str, ...] = ("int32", "uint32", "i32", "u32")


def scoped_time_anchor_paths() -> tuple[str, ...]:
    return tuple(SCOPED_TIME_ANCHOR_PATHS)


def required_time_anchor_files() -> tuple[str, ...]:
    return tuple(REQUIRED_TIME_ANCHOR_FILES)


__all__ = [
    "FORBIDDEN_TICK_WIDTH_TOKENS",
    "REQUIRED_TIME_ANCHOR_FILES",
    "SCOPED_TIME_ANCHOR_PATHS",
    "required_time_anchor_files",
    "scoped_time_anchor_paths",
]
