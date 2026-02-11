import argparse
import json
import os
import subprocess
import sys


def _run(cmd, cwd):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(description="ControlX prompt sanitizer tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    prompt = "\n".join(
        [
            "stop on failure",
            "please advise",
            "tool_ui_bind --check",
            "scripts/ci/check_repox_rules.py --repo-root .",
            "python tools/performx/performx.py run",
            "real requested change: update docs only",
            "",
        ]
    )
    cmd = [
        sys.executable,
        os.path.join(repo_root, "tools", "controlx", "controlx.py"),
        "sanitize",
        "--repo-root",
        repo_root,
        "--prompt-text",
        prompt,
    ]
    result = _run(cmd, cwd=repo_root)
    if result.returncode != 0:
        print(result.stdout)
        return 1
    try:
        payload = json.loads(result.stdout or "{}")
    except ValueError:
        print(result.stdout)
        return 1

    if payload.get("result") != "sanitized":
        print(result.stdout)
        return 1
    sanitized_prompt = str(payload.get("sanitized_prompt", ""))
    forbidden_tokens = (
        "stop on failure",
        "please advise",
        "tool_ui_bind",
        "check_repox_rules.py",
        "performx.py",
    )
    for token in forbidden_tokens:
        if token in sanitized_prompt.lower():
            print("token leaked after sanitation: {}".format(token))
            return 1
    execution_plan = payload.get("execution_plan", [])
    joined = " ".join(execution_plan).lower()
    if "gate.py precheck" not in joined or "gate.py exitcheck" not in joined:
        print("execution plan missing canonical gate path")
        print(result.stdout)
        return 1
    if not isinstance(payload.get("sanitization_actions"), list):
        print("sanitization actions missing")
        return 1
    print("prompt_sanitizer_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
