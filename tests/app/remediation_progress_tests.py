import argparse
import os
import sys


def _load_gate_module(repo_root):
    dev_root = os.path.join(repo_root, "scripts", "dev")
    if dev_root not in sys.path:
        sys.path.insert(0, dev_root)
    import gate

    return gate


def main():
    parser = argparse.ArgumentParser(description="Remediation progress invariant tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    gate = _load_gate_module(repo_root)

    before = {
        "returncode": 1,
        "output": "INV-TOOLS-DIR-MISSING INV-TOOL-UNRESOLVABLE error error",
    }
    after_better = {
        "returncode": 1,
        "output": "INV-TOOL-UNRESOLVABLE error",
    }
    after_worse = {
        "returncode": 1,
        "output": "INV-TOOLS-DIR-MISSING INV-TOOL-UNRESOLVABLE error error error",
    }
    after_fixed = {
        "returncode": 0,
        "output": "",
    }

    if not gate._has_measurable_progress(before, after_better):
        raise RuntimeError("expected measurable progress for lower failure score")
    if gate._has_measurable_progress(before, after_worse):
        raise RuntimeError("unexpected measurable progress for higher failure score")
    if not gate._has_measurable_progress(before, after_fixed):
        raise RuntimeError("expected measurable progress for successful remediation")

    tool_strategies = gate._default_strategy_classes("TOOL_DISCOVERY")
    if len(tool_strategies) < 2:
        raise RuntimeError("strategy diversity contract violated for TOOL_DISCOVERY")

    print("remediation_progress_invariant=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
