import argparse
import hashlib
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


def _compatx(repo_root, args):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "compatx", "compatx.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, repo_root)


def _payload_hash(path):
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description="CompatX migration tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="compatx-migrate-") as temp_dir:
        input_path = os.path.join(temp_dir, "input.json")
        output_a = os.path.join(temp_dir, "output_a.json")
        output_b = os.path.join(temp_dir, "output_b.json")

        with open(input_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(
                {
                    "schema_id": "dominium.schema.save_format",
                    "schema_version": "1.0.0",
                    "save_id": "fixture.save",
                    "extensions": {},
                },
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")

        base_args = [
            "migrate",
            "--migration-id",
            "migration.save_format.1_0_0_to_1_1_0",
            "--input-json",
            input_path,
        ]
        result_a = _compatx(repo_root, base_args + ["--output-json", output_a])
        result_b = _compatx(repo_root, base_args + ["--output-json", output_b])
        if result_a.returncode != 0:
            print(result_a.stdout)
            return 1
        if result_b.returncode != 0:
            print(result_b.stdout)
            return 1

        hash_a = _payload_hash(output_a)
        hash_b = _payload_hash(output_b)
        if hash_a != hash_b:
            print("non-deterministic migration output")
            return 1

        with open(output_a, "r", encoding="utf-8") as handle:
            migrated = json.load(handle)
        if migrated.get("schema_version") != "1.1.0":
            print("migration version mismatch")
            return 1

    print("compatx_migration_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

