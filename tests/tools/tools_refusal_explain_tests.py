import argparse
import json
import os
import subprocess
import sys
import tempfile


def run_fab_validate(repo_root, input_path):
    script = os.path.join(repo_root, "tools", "fab", "fab_validate.py")
    cmd = [sys.executable, script, "--input", input_path, "--repo-root", repo_root, "--format", "json"]
    result = subprocess.run(cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return json.loads(result.stdout.decode("utf-8"))


def run_refusal_explain(repo_root, input_path, data_path):
    script = os.path.join(repo_root, "tools", "inspect", "refusal_explain.py")
    cmd = [sys.executable, script, "--input", input_path, "--data", data_path, "--repo-root", repo_root, "--format", "json"]
    output = subprocess.check_output(cmd, cwd=repo_root)
    return json.loads(output.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="refusal_explain tool tests.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    bad_pack = os.path.join(repo_root, "tests", "fab", "fixtures", "fab_pack_bad_interface.json")
    validation = run_fab_validate(repo_root, bad_pack)
    if validation.get("ok"):
        print("expected fab_validate to fail on bad interface fixture")
        return 1

    handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8")
    json.dump(validation, handle, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    handle.close()
    try:
        explained = run_refusal_explain(repo_root, handle.name, bad_pack)
    finally:
        try:
            os.unlink(handle.name)
        except OSError:
            pass

    if "explanations" not in explained or not explained["explanations"]:
        print("refusal_explain missing explanations")
        return 1

    print("refusal_explain OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
