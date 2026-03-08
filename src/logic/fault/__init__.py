"""LOGIC-8 fault helpers."""

from src.logic.fault.fault_engine import (
    PROCESS_LOGIC_FAULT_CLEAR,
    PROCESS_LOGIC_FAULT_SET,
    REFUSAL_LOGIC_FAULT_INVALID,
    REFUSAL_LOGIC_FAULT_SHORT_UNRESOLVED,
    apply_faults_to_signal_value,
    build_logic_fault_state_row,
    logic_fault_kind_rows_by_id,
    normalize_logic_fault_state_rows,
    process_logic_fault_clear,
    process_logic_fault_set,
    select_active_logic_fault_rows,
)

__all__ = [
    "PROCESS_LOGIC_FAULT_CLEAR",
    "PROCESS_LOGIC_FAULT_SET",
    "REFUSAL_LOGIC_FAULT_INVALID",
    "REFUSAL_LOGIC_FAULT_SHORT_UNRESOLVED",
    "apply_faults_to_signal_value",
    "build_logic_fault_state_row",
    "logic_fault_kind_rows_by_id",
    "normalize_logic_fault_state_rows",
    "process_logic_fault_clear",
    "process_logic_fault_set",
    "select_active_logic_fault_rows",
]
