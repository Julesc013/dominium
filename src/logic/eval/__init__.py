"""LOGIC-4 evaluation exports."""

from src.logic.eval.commit_engine import (
    PROCESS_STATEVEC_UPDATE,
    REFUSAL_STATEVEC_UPDATE_INVALID,
    process_statevec_update,
)
from src.logic.eval.logic_eval_engine import (
    PROCESS_LOGIC_NETWORK_EVALUATE,
    REFUSAL_LOGIC_EVAL_LOOP_POLICY,
    REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND,
    REFUSAL_LOGIC_EVAL_NETWORK_NOT_VALIDATED,
    REFUSAL_LOGIC_EVAL_TIMING_VIOLATION,
    normalize_logic_eval_state,
    process_logic_network_evaluate,
)
from src.logic.eval.runtime_state import (
    normalize_logic_eval_record_rows,
    normalize_logic_network_runtime_state_rows,
    normalize_logic_noise_decision_rows,
    normalize_logic_oscillation_record_rows,
    normalize_logic_pending_signal_update_rows,
    normalize_logic_propagation_trace_artifact_rows,
    normalize_logic_security_fail_rows,
    normalize_logic_state_update_record_rows,
    normalize_logic_timing_violation_event_rows,
    normalize_logic_throttle_event_rows,
    normalize_logic_watchdog_timeout_event_rows,
)
from src.logic.eval.sense_engine import build_logic_element_index, build_logic_sense_snapshot

__all__ = [
    "PROCESS_LOGIC_NETWORK_EVALUATE",
    "PROCESS_STATEVEC_UPDATE",
    "REFUSAL_LOGIC_EVAL_LOOP_POLICY",
    "REFUSAL_LOGIC_EVAL_NETWORK_NOT_FOUND",
    "REFUSAL_LOGIC_EVAL_NETWORK_NOT_VALIDATED",
    "REFUSAL_LOGIC_EVAL_TIMING_VIOLATION",
    "REFUSAL_STATEVEC_UPDATE_INVALID",
    "build_logic_element_index",
    "build_logic_sense_snapshot",
    "normalize_logic_eval_record_rows",
    "normalize_logic_eval_state",
    "normalize_logic_network_runtime_state_rows",
    "normalize_logic_noise_decision_rows",
    "normalize_logic_oscillation_record_rows",
    "normalize_logic_pending_signal_update_rows",
    "normalize_logic_propagation_trace_artifact_rows",
    "normalize_logic_security_fail_rows",
    "normalize_logic_state_update_record_rows",
    "normalize_logic_timing_violation_event_rows",
    "normalize_logic_throttle_event_rows",
    "normalize_logic_watchdog_timeout_event_rows",
    "process_logic_network_evaluate",
    "process_statevec_update",
]
