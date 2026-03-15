from tools.xstack.testx.tests.performance_envelope_testlib import run_tool


def run(repo_root: str) -> dict:
    for tool_name in (
        "tool_measure_startup.py",
        "tool_measure_memory.py",
        "tool_measure_store_size.py",
    ):
        payload = run_tool(repo_root, tool_name)
        assert payload["exit_code"] == 0
        assert payload["result"] == "complete"
        assert payload["deterministic_fingerprint"]
    return {
        "status": "pass",
        "message": "performance measurement tools run successfully and return deterministic payloads",
    }
