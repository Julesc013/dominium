import argparse
import concurrent.futures
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


def _write_json(path, payload):
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _run_one(repo_root, index):
    with tempfile.TemporaryDirectory(prefix="controlx-par-{:02d}-".format(index)) as temp_dir:
        queue_path = os.path.join(temp_dir, "queue.json")
        audit_root = os.path.join(temp_dir, "audit")
        _write_json(
            queue_path,
            {
                "record": {
                    "queue_id": "controlx.queue.parallel.{}".format(index),
                    "continue_on_mechanical_failure": True,
                    "items": [{"item_id": "item.1", "prompt_text": "noop"}],
                    "extensions": {},
                }
            },
        )
        result = _run(
            [
                sys.executable,
                os.path.join(repo_root, "tools", "controlx", "controlx.py"),
                "run-queue",
                "--repo-root",
                repo_root,
                "--queue-file",
                queue_path,
                "--dry-run",
                "--workspace-id",
                "par-ws-{:02d}".format(index),
                "--audit-root",
                audit_root,
            ],
            cwd=repo_root,
        )
        return int(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="ControlX parallel workspace isolation tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        codes = list(executor.map(lambda idx: _run_one(repo_root, idx), range(1, 11)))
    if any(code != 0 for code in codes):
        print("parallel controlx run failed: {}".format(codes))
        return 1

    print("controlx_parallel_workspace_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
