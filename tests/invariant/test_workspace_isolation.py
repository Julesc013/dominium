import argparse
import hashlib
import os
import subprocess
import sys


def _load_helpers(repo_root: str):
    dev_dir = os.path.join(repo_root, "scripts", "dev")
    if dev_dir not in sys.path:
        sys.path.insert(0, dev_dir)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    import env_tools_lib  # pylint: disable=import-error
    from tools.xstack.core.runners import _apply_output_routing  # pylint: disable=import-error

    return env_tools_lib, _apply_output_routing


def _head_sha(repo_root: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError:
        return "nogit"
    if int(proc.returncode) != 0:
        return "nogit"
    return (proc.stdout or "").strip().lower()


def _expected_workspace_id(repo_root: str, head_sha: str) -> str:
    seed = "{}|{}".format(repo_root.replace("\\", "/"), head_sha)
    return "ws-{}".format(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16])


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: XStack workspace isolation uses git-root+HEAD hashing.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)
    env_tools_lib, apply_output_routing = _load_helpers(repo_root)

    head_sha = _head_sha(repo_root)
    expected = _expected_workspace_id(repo_root, head_sha)
    actual = env_tools_lib.canonical_workspace_id(repo_root, env={})
    if expected != actual:
        print("workspace id formula mismatch: expected {} got {}".format(expected, actual))
        return 1

    alt = _expected_workspace_id(repo_root, "deadbeef" * 5)
    if alt == actual:
        print("workspace id collision across distinct HEAD values")
        return 1

    routed = apply_output_routing(
        cmd=["python", "scripts/ci/check_repox_rules.py", "--repo-root", repo_root, "--profile", "FAST"],
        runner_id="repox_runner",
        group_id="",
        repo_root=repo_root,
        snapshot_mode=False,
        workspace_id=actual,
    )
    joined = " ".join(str(item) for item in routed).replace("\\", "/")
    expected_fragment = "/.xstack_cache/{}/artifacts/".format(actual)
    if expected_fragment not in joined:
        print("runner output root is not workspace-scoped: {}".format(joined))
        return 1

    print("workspace isolation invariant OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
