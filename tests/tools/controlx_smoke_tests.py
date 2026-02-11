import argparse
import json
import os
import subprocess
import sys
import tempfile


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


def _controlx(repo_root, args):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "controlx", "controlx.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, cwd=repo_root)


def main():
    parser = argparse.ArgumentParser(description="ControlX smoke test.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="controlx-smoke-") as temp_dir:
        queue_path = os.path.join(temp_dir, "queue.json")
        audit_root = os.path.join(temp_dir, "audit")
        payload = {
            "schema_id": "dominium.schema.governance.controlx_queue",
            "schema_version": "1.0.0",
            "record": {
                "queue_id": "controlx.smoke.queue",
                "continue_on_mechanical_failure": True,
                "items": [
                    {
                        "item_id": "smoke.1",
                        "prompt_text": "run scripts/ci/check_repox_rules.py and then continue",
                    }
                ],
                "extensions": {},
            },
        }
        with open(queue_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")

        result = _controlx(
            repo_root,
            [
                "run-queue",
                "--queue-file",
                queue_path,
                "--dry-run",
                "--audit-root",
                audit_root,
            ],
        )
        if result.returncode != 0:
            print(result.stdout)
            return 1
        try:
            parsed = json.loads(result.stdout or "{}")
        except ValueError:
            print(result.stdout)
            return 1
        if parsed.get("result") != "queue_complete":
            print(result.stdout)
            return 1
        runs = parsed.get("runs", [])
        if not isinstance(runs, list) or len(runs) != 1:
            print(result.stdout)
            return 1
        runlog_rel = str(runs[0].get("runlog", "")).strip()
        if not runlog_rel:
            print(result.stdout)
            return 1
        runlog_path = os.path.join(repo_root, runlog_rel.replace("/", os.sep))
        if not os.path.isfile(runlog_path):
            print("missing runlog {}".format(runlog_path))
            return 1
        with open(runlog_path, "r", encoding="utf-8") as handle:
            runlog = json.load(handle)
        for step in runlog.get("gate_steps", []):
            command = str(step.get("command", "")).lower()
            if "tool_ui_bind" in command or "check_repox_rules.py" in command or "ctest" in command:
                print("unexpected direct gate/tool call in runlog command {}".format(command))
                return 1
        print("controlx_smoke=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
