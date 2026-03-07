"""LOGIC-5 timing exports."""

from src.logic.timing.oscillation_engine import (
    build_logic_timing_state_hash,
    detect_network_oscillation,
)
from src.logic.timing.pattern_engine import (
    build_watchdog_definition_row,
    detect_watchdog_timeout_transitions,
    normalize_watchdog_definition_rows,
    synchronizer_stage_count,
    timing_pattern_id_for_element,
    watchdog_definition_rows_by_id,
)

__all__ = [
    "build_logic_timing_state_hash",
    "build_watchdog_definition_row",
    "detect_watchdog_timeout_transitions",
    "detect_network_oscillation",
    "normalize_watchdog_definition_rows",
    "synchronizer_stage_count",
    "timing_pattern_id_for_element",
    "watchdog_definition_rows_by_id",
]
