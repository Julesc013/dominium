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
    parser = argparse.ArgumentParser(description="ControlX workspace isolation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="controlx-workspace-") as temp_dir:
        queue_path = os.path.join(temp_dir, "queue.json")
        audit_root = os.path.join(temp_dir, "audit")
        payload = {
            "record": {
                "queue_id": "controlx.workspace.queue",
                "continue_on_mechanical_failure": True,
                "items": [
                    {"item_id": "ws.1", "prompt_text": "client ui update"},
                    {"item_id": "ws.2", "prompt_text": "server docs update"},
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
        ]
        result = _run(cmd, cwd=repo_root)
        if result.returncode != 0:
            print(result.stdout)
            return 1
        parsed = json.loads(result.stdout or "{}")
        runs = parsed.get("runs", [])
        if len(runs) != 2:
            print(result.stdout)
            return 1
        ws_ids = [str(item.get("workspace_id", "")).strip() for item in runs]
        if len(set(ws_ids)) != 2:
            print("workspace ids must be distinct")
            print(result.stdout)
            return 1
        for ws_id in ws_ids:
            build_root = os.path.join(repo_root, "out", "build", ws_id)
            dist_root = os.path.join(repo_root, "dist", "ws", ws_id)
            if not os.path.isdir(build_root):
                print("missing workspace build root {}".format(build_root))
                return 1
            if not os.path.isdir(dist_root):
                print("missing workspace dist root {}".format(dist_root))
                return 1
        print("workspace_isolation_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
