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


def _compatx(repo_root, args):
    cmd = [sys.executable, os.path.join(repo_root, "tools", "compatx", "compatx.py")]
    cmd.extend(args)
    cmd.extend(["--repo-root", repo_root])
    return _run(cmd, repo_root)


def _write_schema(path, schema_id, schema_version, required_rows):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("SCHEMA: test/example.schema\n")
        handle.write("schema_id: {}\n".format(schema_id))
        handle.write("schema_version: {}\n".format(schema_version))
        handle.write("stability: core\n\n")
        handle.write("record example\n")
        handle.write("  required:\n")
        for row in required_rows:
            handle.write("    - {}: tag\n".format(row))


def main():
    parser = argparse.ArgumentParser(description="CompatX schema diff classification tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    with tempfile.TemporaryDirectory(prefix="compatx-schema-diff-") as temp_dir:
        old_schema = os.path.join(temp_dir, "old.schema")
        new_schema = os.path.join(temp_dir, "new.schema")
        breaking_schema = os.path.join(temp_dir, "breaking.schema")

        _write_schema(old_schema, "dominium.schema.example", "1.0.0", ["alpha", "beta"])
        _write_schema(new_schema, "dominium.schema.example", "1.1.0", ["alpha", "beta", "gamma"])
        _write_schema(breaking_schema, "dominium.schema.example", "2.0.0", ["alpha"])

        ok_result = _compatx(
            repo_root,
            ["schema-diff", "--old-schema", old_schema, "--new-schema", new_schema],
        )
        if ok_result.returncode != 0:
            print(ok_result.stdout)
            return 1
        try:
            ok_payload = json.loads(ok_result.stdout or "{}")
        except ValueError:
            print(ok_result.stdout)
            return 1
        if ok_payload.get("compatibility") != "backward_compatible":
            print(ok_result.stdout)
            return 1

        breaking_result = _compatx(
            repo_root,
            ["schema-diff", "--old-schema", old_schema, "--new-schema", breaking_schema],
        )
        if breaking_result.returncode == 0:
            print("expected breaking schema diff to return non-zero")
            print(breaking_result.stdout)
            return 1
        try:
            breaking_payload = json.loads(breaking_result.stdout or "{}")
        except ValueError:
            print(breaking_result.stdout)
            return 1
        if breaking_payload.get("compatibility") != "breaking":
            print(breaking_result.stdout)
            return 1

    print("compatx_schema_diff_tests=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

