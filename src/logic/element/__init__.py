"""LOGIC-2 element definition and validation exports."""

from src.logic.element.instrumentation_binding import (
    LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID,
    LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND,
    observe_logic_element_output_port,
    observe_logic_element_state_vector,
    resolve_logic_element_instrumentation_surface,
    route_logic_element_forensics,
)
from src.logic.element.logic_element_validator import (
    REFUSAL_LOGIC_INVALID_ELEMENT_DEFINITION,
    build_logic_behavior_model_row,
    build_logic_element_definition_row,
    build_state_machine_definition_row,
    normalize_logic_behavior_model_rows,
    normalize_logic_element_definition_rows,
    normalize_state_machine_definition_rows,
    validate_logic_element_definitions,
)

__all__ = [
    "LOGIC_ELEMENT_INSTRUMENTATION_DEFAULT_ID",
    "LOGIC_ELEMENT_INSTRUMENTATION_OWNER_KIND",
    "REFUSAL_LOGIC_INVALID_ELEMENT_DEFINITION",
    "build_logic_behavior_model_row",
    "build_logic_element_definition_row",
    "build_state_machine_definition_row",
    "normalize_logic_behavior_model_rows",
    "normalize_logic_element_definition_rows",
    "normalize_state_machine_definition_rows",
    "observe_logic_element_output_port",
    "observe_logic_element_state_vector",
    "resolve_logic_element_instrumentation_surface",
    "route_logic_element_forensics",
    "validate_logic_element_definitions",
]
