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


def main():
    parser = argparse.ArgumentParser(description="ControlX queue continuation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="controlx-queue-") as temp_dir:
        queue_path = os.path.join(temp_dir, "queue.json")
        audit_root = os.path.join(temp_dir, "audit")
        payload = {
            "record": {
                "queue_id": "controlx.queue.continue",
                "continue_on_mechanical_failure": True,
                "items": [
                    {"item_id": "q.1", "prompt_text": "docs update 1"},
                    {"item_id": "q.2", "prompt_text": "docs update 2"},
                    {"item_id": "q.3", "prompt_text": "docs update 3"},
                ],
                "extensions": {},
            }
        }
        with open(queue_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")

        cmd = [
            sys.executable,
            os.path.join(repo_root, "tools", "controlx", "controlx.py"),
            "run-queue",
            "--repo-root",
            repo_root,
            "--queue-file",
            queue_path,
            "--dry-run",
            "--audit-root",
            audit_root,
            "--simulate-mechanical-failure-index",
            "2",
        ]
        result = _run(cmd, cwd=repo_root)
        if result.returncode != 0:
            print(result.stdout)
            return 1
        parsed = json.loads(result.stdout or "{}")
        if parsed.get("result") != "queue_complete":
            print(result.stdout)
            return 1
        runs = parsed.get("runs", [])
        if len(runs) != 3:
            print(result.stdout)
            return 1
        statuses = [str(item.get("status", "")).strip() for item in runs]
        if "pass" not in statuses:
            print("expected pass statuses")
            print(result.stdout)
            return 1
        if any(status == "semantic_escalation_required" for status in statuses):
            print("unexpected semantic escalation")
            print(result.stdout)
            return 1
        print("queue_continue_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
