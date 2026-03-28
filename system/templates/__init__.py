"""SYS-4 template compiler exports."""

from system.templates.template_compiler import (
    REFUSAL_TEMPLATE_CYCLE,
    REFUSAL_TEMPLATE_FORBIDDEN_MODE,
    REFUSAL_TEMPLATE_INVALID,
    REFUSAL_TEMPLATE_MISSING_DOMAIN,
    REFUSAL_TEMPLATE_MISSING_REFERENCE,
    REFUSAL_TEMPLATE_NOT_FOUND,
    REFUSAL_TEMPLATE_SPEC_NONCOMPLIANT,
    SystemTemplateCompileError,
    build_system_template_row,
    compile_system_template,
    normalize_system_template_rows,
    resolve_nested_template_order,
    system_template_rows_by_id,
)

__all__ = [
    "REFUSAL_TEMPLATE_INVALID",
    "REFUSAL_TEMPLATE_NOT_FOUND",
    "REFUSAL_TEMPLATE_MISSING_REFERENCE",
    "REFUSAL_TEMPLATE_MISSING_DOMAIN",
    "REFUSAL_TEMPLATE_CYCLE",
    "REFUSAL_TEMPLATE_FORBIDDEN_MODE",
    "REFUSAL_TEMPLATE_SPEC_NONCOMPLIANT",
    "SystemTemplateCompileError",
    "build_system_template_row",
    "normalize_system_template_rows",
    "system_template_rows_by_id",
    "resolve_nested_template_order",
    "compile_system_template",
]
