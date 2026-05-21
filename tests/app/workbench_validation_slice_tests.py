import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from apps.workbench.module.validation.command import (  # noqa: E402
    COMMAND_ID,
    DIAG_INVALID_INPUT,
    DIAG_VALIDATION_WARNING,
    REFUSAL_INVALID_TARGET,
    run_validation_command,
)
from apps.workbench.module.validation.workbench_projection import (  # noqa: E402
    project_result_table,
    project_validation_run,
    validation_module_descriptor,
)


class FakeValidationService:
    def __init__(self, report):
        self.report = report
        self.calls = []

    def run_validation(self, request):
        self.calls.append(dict(request))
        return {
            "service_id": "service.validation.fake",
            "report": self.report,
            "evidence": ["tests/app/fixtures/fake_validation_report.json"],
            "written_outputs": {},
        }


def _report(result="complete", warnings=None, errors=None):
    warnings = list(warnings or [])
    errors = list(errors or [])
    return {
        "schema_version": "1.0.0",
        "validation_id": "validation.pipeline.validation.pipeline.v1.fast",
        "suite_id": "validate.all",
        "category_id": "validate.aggregate",
        "profile": "FAST",
        "result": result,
        "message": "validation pipeline test result",
        "suite_order": 0,
        "adapter_id": "validation_engine",
        "description": "Unified validation aggregate for test.",
        "checked_paths": ["contracts/registry/validation_suite_registry.json"],
        "errors": errors,
        "warnings": warnings,
        "metrics": {"suite_count": 1},
        "fingerprints": {"suite_registry_hash": "a" * 64},
        "legacy_adapters": [],
        "suite_results": [
            {
                "schema_version": "1.0.0",
                "validation_id": "validation.validate.schemas.fast",
                "suite_id": "validate.schemas",
                "category_id": "validate.schemas",
                "profile": "FAST",
                "result": result,
                "message": "schema validation test result",
                "suite_order": 10,
                "adapter_id": "compatx_schema_suite",
                "description": "Validate governed JSON schemas.",
                "checked_paths": ["schemas"],
                "errors": errors,
                "warnings": warnings,
                "metrics": {"finding_count": len(errors) + len(warnings)},
                "fingerprints": {},
                "legacy_adapters": [],
                "suite_results": [],
                "deterministic_fingerprint": "b" * 64,
                "extensions": {},
            }
        ],
        "deterministic_fingerprint": "c" * 64,
        "extensions": {
            "report_json_path": "data/audit/validation_report_FAST.json",
            "report_doc_path": "docs/audit/VALIDATION_REPORT_FAST.md",
        },
    }


def _assert(condition, message, violations):
    if not condition:
        violations.append(message)


def test_command_and_workbench_projection_share_semantics(violations):
    warning = {
        "code": "warn.validation.test",
        "path": "contracts/registry/validation_suite_registry.json",
        "message": "fixture warning",
        "suite_id": "validate.schemas",
        "severity": "warn",
    }
    report = _report(warnings=[warning])
    cli_service = FakeValidationService(report)
    workbench_service = FakeValidationService(report)

    cli_result = run_validation_command(
        {"target": "all", "profile": "FAST", "surface": "cli"},
        service=cli_service,
        invocation_surface="cli",
    )
    workbench_result = project_validation_run({"target": "all", "profile": "FAST"}, service=workbench_service)

    _assert(cli_result["command_id"] == COMMAND_ID, "CLI command id mismatch", violations)
    _assert(workbench_result["command_id"] == COMMAND_ID, "Workbench command id mismatch", violations)
    _assert(cli_result["status"] == "warning", "CLI warning status not preserved", violations)
    _assert(workbench_result["status"] == "warning", "Workbench warning status not preserved", violations)
    _assert(cli_result["diagnostics"][0]["code"] == DIAG_VALIDATION_WARNING, "CLI diagnostic code mismatch", violations)
    _assert(workbench_result["diagnostics"][0]["code"] == DIAG_VALIDATION_WARNING, "Workbench diagnostic code mismatch", violations)
    _assert(cli_result["evidence"] == workbench_result["evidence"], "evidence parity mismatch", violations)
    _assert(cli_service.calls[0]["surface"] == "cli", "CLI surface not normalized", violations)
    _assert(workbench_service.calls[0]["surface"] == "workbench", "Workbench surface not normalized", violations)

    table = project_result_table(workbench_result)
    _assert(table["command_id"] == COMMAND_ID, "table command id mismatch", violations)
    _assert(table["rows"][0]["suite_id"] == "validate.schemas", "table suite row missing", violations)
    _assert(table["rows"][0]["warning_count"] == 1, "table warning count mismatch", violations)


def test_invalid_target_refuses_without_service_call(violations):
    service = FakeValidationService(_report())
    result = run_validation_command({"target": "unknown.scope", "profile": "FAST"}, service=service)

    _assert(result["status"] == "refused", "invalid target did not refuse", violations)
    _assert(not service.calls, "service was called for invalid target", violations)
    _assert(result["payload"]["refusal"]["code"] == REFUSAL_INVALID_TARGET, "invalid target refusal code mismatch", violations)
    _assert(result["diagnostics"][0]["code"] == DIAG_INVALID_INPUT, "invalid target diagnostic code mismatch", violations)
    _assert("contracts/command/validation_run_input.schema.json" in result["evidence"], "input schema evidence missing", violations)

    table = project_result_table(result)
    _assert(table["rows"][0]["result"] == "refused", "refusal table row missing", violations)


def test_workbench_projection_has_no_private_validator_binding(violations):
    path = REPO_ROOT / "apps" / "workbench" / "module" / "validation" / "workbench_projection.py"
    text = path.read_text(encoding="utf-8")
    _assert("tools.validators" not in text, "Workbench projection imports validators directly", violations)
    _assert("validation_engine" not in text, "Workbench projection binds validation_engine directly", violations)

    descriptor = validation_module_descriptor()
    _assert(descriptor["workspace_runtime_implemented"] is False, "module descriptor claims workspace runtime", violations)
    _assert(descriptor["commands"] == [COMMAND_ID], "module descriptor command mismatch", violations)


def test_cli_path_emits_typed_refusal_json(violations):
    cli = REPO_ROOT / "apps" / "workbench" / "module" / "validation" / "cli.py"
    result = subprocess.run(
        [
            sys.executable,
            str(cli),
            "--repo-root",
            str(REPO_ROOT),
            "--target",
            "unknown.scope",
            "--profile",
            "FAST",
        ],
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    _assert(result.returncode == 1, "CLI invalid target should exit 1", violations)
    try:
        payload = json.loads(result.stdout)
    except ValueError:
        violations.append("CLI stdout was not JSON: {}".format(result.stdout[:200]))
        return
    _assert(payload["command_id"] == COMMAND_ID, "CLI JSON command id mismatch", violations)
    _assert(payload["status"] == "refused", "CLI JSON refusal status mismatch", violations)
    _assert(payload["payload"]["refusal"]["code"] == REFUSAL_INVALID_TARGET, "CLI JSON refusal code mismatch", violations)


def test_touched_contracts_parse_and_expose_slice_fields(violations):
    command_schema = json.loads((REPO_ROOT / "contracts" / "command" / "validation_run_input.schema.json").read_text(encoding="utf-8"))
    diagnostic_registry = json.loads((REPO_ROOT / "contracts" / "diagnostics" / "diagnostic_code.registry.json").read_text(encoding="utf-8"))
    workbench_surface = (REPO_ROOT / "contracts" / "workbench" / "workbench_surface.contract.toml").read_text(encoding="utf-8")
    module_surface = (REPO_ROOT / "contracts" / "module" / "module_surface.contract.toml").read_text(encoding="utf-8")

    properties = command_schema.get("properties", {})
    _assert("profile" in properties, "validation input schema missing profile", violations)
    _assert("surface" in properties, "validation input schema missing surface", violations)
    _assert("emit_reports" in properties, "validation input schema missing emit_reports", violations)

    codes = {entry.get("code") for entry in diagnostic_registry.get("codes", []) if isinstance(entry, dict)}
    _assert("DOM-VALIDATION-RUN-REFUSED" in codes, "run refusal diagnostic not registered", violations)
    _assert("DOM-VALIDATION-RUN-WARNING" in codes, "run warning diagnostic not registered", violations)
    _assert("workspace_runtime_implemented = false" in workbench_surface, "workspace runtime flag changed", violations)
    _assert('implementation_path = "apps/workbench/module/validation"' in module_surface, "module surface path not narrowed", violations)


def main():
    violations = []
    test_command_and_workbench_projection_share_semantics(violations)
    test_invalid_target_refuses_without_service_call(violations)
    test_workbench_projection_has_no_private_validator_binding(violations)
    test_cli_path_emits_typed_refusal_json(violations)
    test_touched_contracts_parse_and_expose_slice_fields(violations)
    if violations:
        for violation in violations:
            print(violation)
        return 1
    print("Workbench validation slice tests OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
