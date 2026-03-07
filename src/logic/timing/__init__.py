"""LOGIC-5 timing exports."""

from src.logic.timing.oscillation_engine import (
    build_logic_timing_state_hash,
    detect_network_oscillation,
)
from src.logic.timing.constraint_engine import (
    declared_timing_constraint,
    evaluate_logic_timing_constraints,
)
from src.logic.timing.compute_hooks import (
    LOGIC_TIMING_COMPUTE_OWNER_KIND,
    build_logic_timing_compute_owner_id,
    request_logic_timing_compute,
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
    "build_logic_timing_compute_owner_id",
    "build_watchdog_definition_row",
    "declared_timing_constraint",
    "detect_watchdog_timeout_transitions",
    "detect_network_oscillation",
    "evaluate_logic_timing_constraints",
    "LOGIC_TIMING_COMPUTE_OWNER_KIND",
    "normalize_watchdog_definition_rows",
    "request_logic_timing_compute",
    "synchronizer_stage_count",
    "timing_pattern_id_for_element",
    "watchdog_definition_rows_by_id",
]
