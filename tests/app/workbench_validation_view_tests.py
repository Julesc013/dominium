import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


from apps.workbench.module.validation.command import (  # noqa: E402
    COMMAND_ID,
    CONTRACT_SCHEMA_SUITE_ID,
    DEFAULT_CONTRACT_SCHEMA_TARGET,
    run_validation_command,
)
from apps.workbench.module.validation.workbench_projection import (  # noqa: E402
    SUMMARY_VIEW_ID,
    SUMMARY_VIEW_BINDING_ID,
    VALIDATION_ACTIONS,
    project_validation_summary,
)


def _assert(condition, message, violations):
    if not condition:
        violations.append(message)


def _validation_result():
    return run_validation_command(
        {
            "target_kind": "contract_schema",
            "target_path": DEFAULT_CONTRACT_SCHEMA_TARGET,
            "suite_id": CONTRACT_SCHEMA_SUITE_ID,
            "profile": "FAST",
            "surface": "workbench",
            "mode": "strict",
        },
        repo_root=str(REPO_ROOT),
        invocation_surface="workbench",
    )


def test_summary_projection_preserves_command_result_semantics(violations):
    result = _validation_result()
    summary = project_validation_summary(result)

    _assert(result["command_id"] == COMMAND_ID, "source command mismatch", violations)
    _assert(summary["command_id"] == COMMAND_ID, "summary command mismatch", violations)
    _assert(summary["view_id"] == SUMMARY_VIEW_ID, "summary view id mismatch", violations)
    _assert(summary["binding_id"] == SUMMARY_VIEW_BINDING_ID, "summary binding id mismatch", violations)
    _assert(summary["source_status"] == result["status"], "source status not preserved", violations)
    _assert(summary["sections"]["counts"] == result["payload"]["summary_counts"], "summary counts not preserved", violations)
    _assert(summary["sections"]["diagnostics"] == result["diagnostics"], "diagnostics not preserved", violations)
    _assert(summary["sections"]["evidence"]["refs"] == result["evidence"], "evidence refs not preserved", violations)
    _assert(
        summary["sections"]["evidence"]["packet"] == result["payload"]["evidence_packet"],
        "evidence packet not preserved",
        violations,
    )
    _assert(summary["private_tool_calls"] is False, "summary projection claims private tool calls", violations)
    _assert(summary["runtime_projection_engine"] is False, "summary projection claims runtime engine", violations)
    _assert(summary["workspace_runtime_implemented"] is False, "summary projection claims workspace runtime", violations)


def test_summary_projection_actions_are_declared_not_private_handlers(violations):
    summary = project_validation_summary(_validation_result())
    actions = summary["actions"]
    action_ids = [item["action_id"] for item in actions]

    _assert(action_ids == VALIDATION_ACTIONS, "summary action ids differ from contract order", violations)
    _assert(
        [item["implementation_status"] for item in actions] == ["contract_only", "contract_only", "command_backed"],
        "summary action implementation status mismatch",
        violations,
    )
    _assert(all("handler_path" not in item for item in actions), "action exposes handler path", violations)
    _assert(all("tools/validators" not in repr(item) for item in actions), "action references private validator path", violations)


def main():
    violations = []
    for test in [
        test_summary_projection_preserves_command_result_semantics,
        test_summary_projection_actions_are_declared_not_private_handlers,
    ]:
        test(violations)
    if violations:
        for violation in violations:
            print(f"FAIL: {violation}")
        return 1
    print("Workbench validation view tests OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
